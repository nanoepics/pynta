
use pyo3::prelude::*;
use pyo3::exceptions;
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

pub(crate) struct BufferFiller{
    //the buffers & their size
    buffers: Vec<Py<PyArray2<u16>>>,
    image_size : [usize;2],
    //an interval to fill buffers at.
    interval : Duration,
    // a usize for tracking which buffer to fill
    frames_filled : Arc<AtomicUsize>,
    //a Watch sender for sending the last filled buffer on.
    // last_frame_notification : watch::Sender<usize>,
    // a signal to notify it needs to stop
    stop_signal : Arc<AtomicBool>
}

fn fill_image(image : &mut [u16], image_size : [usize;2], counter: usize) {
    let tracker : [u16;16*16] = [16;16*16];
    // tracker[8+8*16] =17;
    image.fill((counter % 8) as u16+1);
    // let val = image_index % 16;
    let phase = (counter % 4096) as f32 / 4096.0;
    let location_y = ((0.5+0.8*0.5*((3.0*6.28*phase).sin()))*(image_size[1] as f32)) as usize;
    let location_x = ((0.5+0.8*0.5*((7.0*6.28*phase).cos()))*(image_size[0] as f32)) as usize;
    for y in 0..(16.min(image_size[1]-location_y)){
        for x in 0..(16.min(image_size[0]-location_x)){
            image[(location_y+y)*image_size[0]+(location_x+x)] = tracker[16*y+x];
        }
    }
}

impl BufferFiller {
    pub fn run(self) -> () {
        //we want raw references here, and not have to fetch the GIL everytime so we convert them to references once here. 
        let mut images : Vec<&'static mut [u16]>  = pyo3::Python::with_gil(|py| {
            self.buffers.iter().map(|arr| unsafe {
                std::mem::transmute(arr.as_ref(py).as_slice_mut().unwrap())
            }).collect()
       });
       // let n_pixels = image_size[0]*image_size[1];
       let n_buffers = self.buffers.len();
       //todo this can error out differently? 
       let mut local_counter = 0;
    //    let tracker : [u16;16*16] = [16;16*16];
       let mut last_fill = std::time::Instant::now();
       while !self.stop_signal.load(Ordering::Acquire) {
            let image_index = local_counter % n_buffers;
            fill_image(images[image_index], self.image_size, local_counter);
            local_counter += 1;
            self.frames_filled.store(local_counter, Ordering::Release);
            let now = std::time::Instant::now();
            let elapsed = now-last_fill;
            // println!("{:?}", elapsed);
            if elapsed < self.interval {
                // println!("sleeping for {:?} because now = {:?} and last = {:?}", self.interval-elapsed, now, last_fill);
                std::thread::sleep(self.interval-elapsed);
            }
            last_fill = std::time::Instant::now();            
        }
    }
}


pub(crate) struct FrameProcessor {
    //the pybuffers themselves
    buffers: Vec<Py<PyArray2<u16>>>,
    // a usize to track the last processed frame with.
    frames_processed : usize,
    // the callable to apply to them
    callable : PyObject,
    // a Watch receiver for tracking the last value written.
    // last_frame_notification : watch::Receiver<usize>,
    frames_filled : Arc<AtomicUsize>,
    // a signal to notify it needs to stop
    // stop_signal : watch::Receiver<()>
    stop_signal : Arc<AtomicBool>
}

impl FrameProcessor {
    //NOTE: if the buffer filler is too fast we get a race condition here. that also happens with real cameras unfortunately like the hamamatsu
    // the solution is to either use a camera whose API supports read-write locking frames like the Basler, or to copy the frame, check that it's 
    pub fn run(mut self) -> () {
        
       // let n_pixels = image_size[0]*image_size[1];
       let n_buffers = self.buffers.len();
       while !self.stop_signal.load(Ordering::Acquire) {
           //first check that a frame has been filled
           if self.frames_processed < self.frames_filled.load(Ordering::Acquire) {
            //then grab the GIL so we can call python
            pyo3::Python::with_gil(|py| {
                //as this might take some time, regrab the filled frame count
                let mut n_filled = self.frames_filled.load(Ordering::Acquire);
                //and do this in a loop as to prioritize frame processing and keep GIL switching to a minimum.
                while self.frames_processed < n_filled {
                    let n_frames_in_loop = n_filled-self.frames_processed;
                    // println!("{} frames filled, processed {}, so now {} in loop", n_filled, n_frames_in_loop, self.frames_processed);
                    if n_frames_in_loop >= n_buffers {
                        eprintln!("Buffer overflow detetcted! saw {} new frames but the buffer size is {}", n_frames_in_loop, n_buffers);
                    } else {
                        let start_index = self.frames_processed % n_buffers;
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
                    // self.frames_processed = n_filled;
                    let new_filled = self.frames_filled.load(Ordering::Acquire);
                    if new_filled + 1 - self.frames_processed >= n_buffers {
                        eprintln!("possible overflow! filler caught up to processor while processing!")
                    }
                    self.frames_processed = n_filled;
                    n_filled = new_filled;
                }
            });
            // println!("releasing GIL");
           }
           std::thread::yield_now();
       }
    }
}


pub(crate) struct Terminator {
    stop_signal : Arc<AtomicBool>,
    handles: Vec<JoinHandle<()>>
}

impl Terminator {
    pub fn stop(self) {
        println!("terminator sending a stop...");
        self.stop_signal.store(true, Ordering::Release);
        println!("awaiting join handles...");
        for h in self.handles{
            h.join().unwrap();
        }
        println!("everything joined!");
    }
}

#[pyclass(name="DummyCamera")]
pub struct DummyCamera {
    // pub(crate) last_frame : usize,
    pub(crate) roi: ([usize;2],[usize;2]),
    pub(crate) streamer : Option<Terminator>,
    
}



impl DummyCamera {
    pub fn new() -> PyResult<Self> {
        Ok(Self {
            // last_frame : 0,
            roi: ([0,2048],[0, 2048]),
            streamer: None
        })
    }

    pub fn get_roi(&self) -> ([usize;2], [usize;2]) {
        self.roi
    }

    pub fn get_size(&self) -> [usize;2]{
        let roi = self.get_roi();
        [roi.0[1]-roi.0[0], roi.1[1]-roi.1[0]]
    }

    pub fn fill_buffer(&mut self, buffer : &mut [u16]) {
        let buffer_size = self.get_size();
        assert_eq!(buffer.len(), buffer_size[0]*buffer_size[1]);
        // let phase_offset = (self.last_frame % 128) as f64 / 127.0;
       fill_image(buffer, buffer_size, 0);
    }

    pub fn start_stream(&mut self, n_buffers : usize, callable : PyObject) -> PyResult<()>{
        if !Python::with_gil(|py| {callable.as_ref(py).is_callable()}){
            Err(exceptions::PyValueError::new_err(
                format!("Object {:?} is not callable!",callable)
            ))
        } else {
            let image_size = self.get_size();
            let buffers = Python::with_gil(|py| vec![PyArray2::zeros(py, [image_size[1], image_size[0]], false).to_owned(); n_buffers]);
            // println!("firing up the reactor...");
            // crate::REACTOR.block_on(async {
            // let (stop_send, stop_receiver) = watch::channel(());
            let stop_signal = Arc::new(AtomicBool::new(false));
            let fill_counter = Arc::new(AtomicUsize::new(0));
            let interval = std::time::Duration::from_millis(5);
            let filler = BufferFiller {
                buffers : buffers.clone(),
                image_size : image_size,
                //an interval to fill buffers at.
                interval,
                // a usize for tracking which buffer to fill
                frames_filled : fill_counter.clone(),
                //a Watch sender for sending the last filled buffer on.
                // last_frame_notification : frame_count_send,
                // a signal to notify it needs to stop
                stop_signal : stop_signal.clone()
            };
            let processor = FrameProcessor {
                //the pybuffers themselves
                buffers,
                // a usize to track the last processed frame with.
                frames_processed : 0,
                // the callable to apply to them
                callable,
                // a Watch receiver for tracking the last value written.
                frames_filled : fill_counter,
                // a signal to notify it needs to stop
                stop_signal : stop_signal.clone()
            };
            
            self.streamer = Some(Terminator{
                stop_signal : stop_signal,
                handles : vec![
                    std::thread::Builder::new().name("DumnmyCamera-frame-filler".to_string()).spawn(move || filler.run()).unwrap(),
                    std::thread::Builder::new().name("DumnmyCamera-frame-processor".to_string()).spawn(move || processor.run()).unwrap()
                ]
            });
            // });
            println!("done!");
            Ok(())
        }
    }
}