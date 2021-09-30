use pyo3::prelude::*;
use pyo3::exceptions;
use crate::{PyCamera, to_py_err};
use dcam4;
use numpy::{PyArray2};
use std::sync::{
    atomic::{
        AtomicBool,
        AtomicUsize,
        Ordering
    },
    Arc
};
use std::time::Duration;
use std::thread::JoinHandle;

#[pyclass(name="DcamCamera")]
pub struct DcamCamera {
    //the handle is wrapped in an Arc (Atomic reference counter) as we want to clone it to another thread for the frame processor
    //normal borrowing rules via references don't play nicely with python interop and the handle itself is neither clone not copy as it needs to call dcamdev_close 
    dev : Arc<dcam4::Camera>,
    buffers: Vec<Py<PyArray2<u16>>>,
    processor_handle : Option<JoinHandle<()>>,
    stop_signal : Arc<AtomicBool>
}

pub struct FrameProcessor{
    //the camera handle for fetching the frames
    dev : Arc<dcam4::Camera>,
    //the pybuffers themselves
    buffers: Vec<Py<PyArray2<u16>>>,
    // a usize to track the last processed frame with.
    frames_processed : usize,
    // the callable to apply to them
    callable : PyObject,
    // a signal to notify it needs to stop
    stop_signal : Arc<AtomicBool>
}

impl FrameProcessor{
    //NOTE: if the buffer filler is too fast we get a race condition here. that also happens with real cameras unfortunately like the hamamatsu
    // the solution is to either use a camera whose API supports read-write locking frames like the Basler, or to copy the frame, check that it's 

    pub fn run(mut self) -> () {
        let handle : &dcam4::Camera = &self.dev;
        // let n_pixels = image_size[0]*image_size[1];
        let n_buffers = self.buffers.len();
        let mut frames_processed = 0;
        while !self.stop_signal.load(Ordering::Acquire) {
            //first check that a frame has been filled
            if frames_processed < (handle.frames_produced().unwrap() as usize) {
             //then grab the GIL so we can call python
             pyo3::Python::with_gil(|py| {
                 //as this might take some time, regrab the filled frame count
                 let mut n_filled = handle.frames_produced().unwrap() as usize;
                 //and do this in a loop as to prioritize frame processing and keep GIL switching to a minimum.
                 while frames_processed < n_filled {
                     let n_frames_in_loop = n_filled-frames_processed;
                     if n_frames_in_loop >= n_buffers {
                         eprintln!("Buffer overflow detetcted! saw {} new frames but the buffer size is {}", n_frames_in_loop, n_buffers);
                     } else {
                         let start_index = frames_processed % n_buffers;
                         let end_index = n_filled % n_buffers;
                         // println!("indices are {} and {}", start_index, end_index);
                         if end_index < start_index {
                             for idx in start_index..n_buffers {
                                 self.callable.call1(py, (&self.buffers[idx],)).unwrap();
                             }
                             for idx in 0..end_index {
                                 self.callable.call1(py, (&self.buffers[idx],)).unwrap();
                             }
                         } else {
                             for idx in start_index..end_index {
                                 self.callable.call1(py, (&self.buffers[idx],)).unwrap();
                             }
                         }
                     } 
                     //update the frames filled and processed count before retrying the loop
                     let new_filled = (handle.frames_produced().unwrap() as usize);
                     if new_filled + 1 - frames_processed >= n_buffers {
                         eprintln!("possible overflow! filler caught up to processor while processing!")
                     }
                     frames_processed = n_filled;
                     n_filled = new_filled;
                 }
             });
             // println!("releasing GIL");
            }
            handle.wait_for_next_frame_timeout(100);
        }
     }
}

impl DcamCamera{
    pub fn new() -> PyResult<Self> {
        Ok(Self{
            dev: Arc::new(dcam4::Camera::new()),
            buffers: vec![],
            processor_handle : None,
            stop_signal : Arc::new(AtomicBool::new(false))
        })
    }

    pub fn get_mut_handle(&mut self) -> PyResult<&mut dcam4::Camera> {
        Arc::get_mut(&mut self.dev).ok_or(exceptions::PyException::new_err("dcam camera can't be modified as it is already borrowed. (is a capture running?)"))

    }

    // pub fn get_handle(&self) -> PyResult<&mut dcam4::Camera> {
    //     Arc::get_mut(&mut self.dev).ok_or(exceptions::PyException::new_err("dcam camera can't be modified as it is already borrowed. (is a capture running?)"))
    // }
}

impl PyCamera for DcamCamera{
    fn snap_into(&mut self, arr : &PyArray2<u16>) -> PyResult<()> {
        to_py_err(self.get_mut_handle()?.snap_into(unsafe{arr.as_slice_mut()?}))
    }
    fn start_stream(&mut self, n_buffers : usize, callable : PyObject) -> PyResult<()> {
        if !Python::with_gil(|py| {callable.as_ref(py).is_callable()}){
            Err(exceptions::PyValueError::new_err(
                format!("Object {:?} is not callable!",callable)
            ))
        } else {
            self.stop_signal.store(false, Ordering::Release);
            let image_size = self.get_size()?;
            let mut raw_buffers : Vec<&'static mut [u16]> = Python::with_gil(|py| { 
                self.buffers = vec![PyArray2::zeros(py, [image_size[1], image_size[0]], false).to_owned(); n_buffers];
                self.buffers.iter().map(|arr| unsafe {
                    std::mem::transmute(arr.as_ref(py).as_slice_mut().unwrap())
                }).collect() 
            });
            to_py_err(self.get_mut_handle()?.start_streaming_into(raw_buffers.as_mut_slice()))?;
            let processor = FrameProcessor {
                //the pybuffers themselves
                buffers: self.buffers.clone(),
                // a usize to track the last processed frame with.
                frames_processed : 0,
                // the callable to apply to them
                callable,
                // a Watch receiver for tracking the last value written.
                dev: self.dev.clone(),
                // a signal to notify it needs to stop
                stop_signal : self.stop_signal.clone()
            };
            self.processor_handle = Some(std::thread::Builder::new().name("Dcam-frame-processor".to_string()).spawn(move || processor.run()).unwrap());
            Ok(())
        }
    }

    fn stop_stream(&mut self) -> PyResult<()> {
        if self.is_streaming()? {
            {
                self.stop_signal.store(true, Ordering::Release);
                to_py_err(self.processor_handle.take().unwrap().join())?;
            }
            to_py_err(self.get_mut_handle()?.stop_stream())
        } else {
            Ok(())
        }
        
    }
    fn set_roi(&mut self, x : [usize;2], y : [usize;2]) -> PyResult<([usize;2], [usize;2])>{
        to_py_err(self.get_mut_handle()?.set_region_of_interest((x[0], x[1]), (y[0], y[1])))?;
        self.get_roi()
    }    

    fn get_roi(&self) -> PyResult<([usize;2], [usize;2])> {
        let (x,y) =  to_py_err(self.dev.get_region_of_interest())?;
        Ok(([x.0, x.1], [y.0, y.1]))
    }

    fn set_exposure(&mut self, exposure_in_seconds: f64) -> PyResult<f64> {
        to_py_err(
            self.get_mut_handle()?
            .set_exposure(std::time::Duration::from_secs_f64(exposure_in_seconds))
            .map(|duration|{duration.as_secs_f64()})
        )  
    }
    fn get_exposure(&self) -> PyResult<f64> {
        to_py_err(self.dev.get_exposure().map(|duration|{duration.as_secs_f64()}))
    }

    fn get_max_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }

    fn is_streaming(&self) -> PyResult<bool> {
        Ok(self.processor_handle.is_some())
    }
}