
use pyo3::prelude::*;
use pyo3::exceptions;
use numpy::{PyArray2};
use std::sync::mpsc;
use std::thread;

// pub(crate) struct CameraStreamer<T: Copy>{
//     pub(crate) buffers : Vec<Py<PyArray2<T>>>,
//     // last_frame = 
//     pub(crate) frame_processor : PyObject, //must be callable
//     pub(crate) last_frame_id : usize,//std::sync::atomic::AtomicUsize,
//     pub(crate) buffer_size : [usize;3],
// }

// pub(crate) struct StreamHandle{
//     pub(crate) join_handle : thread::JoinHandle<()>,
//     pub(crate) stop_signal : mpsc::SyncSender<()>
// }



// impl StreamHandle {
//     pub fn stop(self) -> () {
//         println!("sending stop signal!");
//         self.stop_signal.send(()).unwrap();
//         println!("waiting on join...!");
//         let ret = self.join_handle.join().unwrap();
//         println!("stream stopped.");
//         ret
//     }
// }

use std::sync::atomic::{AtomicBool,AtomicUsize};
use std::sync::atomic::Ordering;
use std::sync::Arc;
use std::time::Duration;
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
    //    loop { tokio::select!{
    //        _ = self.stop_signal.changed() => {println!("Filler stopping!"); return},
    //        _instant = self.interval.tick() => {
    //         //    let now = std::time::Instant::now();
    //             // println!("ticked at {:?}, now {:?}", instant, now);
    //             let image_index = self.last_frame_id % n_buffers;
    //             // let mut slice = self.buffers.index_axis_mut(Axis(0), image_index);//[n_pixels*image_index..n_pixels*(image_index+1)];
    //             let phase_offset = (self.last_frame_id % 128) as f64 / 127.0;
    //             for y in 0..self.image_size[1]{ 
    //                 let yf = (y as f64)/((self.image_size[0]-1) as f64);
    //                 for x in 0..self.image_size[0]{
    //                     let xf = (x as f64)/((self.image_size[0]-1) as f64);
    //                     let val = 350.0*(0.5+0.5*((xf+yf+phase_offset)*6.28).sin());
    //                     images[image_index][y*self.image_size[0]+x] = val.max(0.0) as u16;
    //                 }
    //             }
    //             match self.last_frame_notification.send(self.last_frame_id) {
    //                 Ok(_) => {
    //                     // tokio::task::yield_now().await;
    //                 }
    //                 Err(_) => {return;}
    //             }
    //             self.last_frame_id += 1;
    //        }
    //    }};
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
            std::thread::yield_now();
           }
       }
       //todo this can error out differently? 
    //    loop { tokio::select!{
    //        _new_frame = self.last_frame_notification.changed() => {
    //            let new_frame_id : usize= *self.last_frame_notification.borrow();
    //         //    println!("saw frame_id {}", new_frame_id);
    //            let n_frames = new_frame_id + 1 - self.next_frame_to_process;
    //            if n_frames > n_buffers {
    //                eprintln!("Buffer overflow detetcted! saw {} new frames but the buffer size is {}", n_frames, n_buffers);
    //            } else {
    //              let start_index = self.next_frame_to_process % n_buffers;
    //              let end_index = new_frame_id % n_buffers;
    //              println!("saw {} new frames!", n_frames);
    //              pyo3::Python::with_gil(|py| {
    //                 if end_index < start_index {
    //                     for idx in start_index..n_buffers {
    //                         self.callable.call1(py, (&self.buffers[idx],));
    //                     }
    //                     for idx in 0..end_index {
    //                         self.callable.call1(py, (&self.buffers[idx],));
    //                     }
    //                 } else {
    //                     for idx in 0..end_index {
    //                         self.callable.call1(py, (&self.buffers[idx],));
    //                     }
    //                 }
    //              });
    //            }
    //            self.next_frame_to_process = new_frame_id+1;
    //        },
    //        _ = self.stop_signal.changed() => {  println!("processor stopping!"); return }
    //    }};

    // }
    }
}

use std::thread::JoinHandle;

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

// impl CameraStreamer<u16> {
//     pub fn new(callable : PyObject, n_buffers : usize, image_size : [usize;2]) -> PyResult<Self> {
//         if !Python::with_gil(|py| {callable.as_ref(py).is_callable()}){
//             Err(exceptions::PyValueError::new_err(
//                 format!("Object {:?} is not callable!",callable)
//             ))
//         } else {
//             Ok(Self{
//                 buffers : Python::with_gil(|py| vec![PyArray2::zeros(py, [image_size[1], image_size[0]], false).to_owned(); n_buffers]),
//                 frame_processor : callable,
//                 last_frame_id : 0,
//                 buffer_size : [n_buffers, image_size[1], image_size[0]]
//             })
//         }
//     }

//     pub fn start(mut self) -> StreamHandle {
//         let (tx, rx) = mpsc::sync_channel::<()>(1);
//         StreamHandle{
//             stop_signal : tx,
//             join_handle : std::thread::spawn(move || {
//                 //grab all the pointers to the numpy arrays data, and convert them to static references.
//                 //this is highly unsafe (in the rust sense) but it is safe here as we keep the buffers alive (and pinned) for as long as they are 
//                 //used here. They will mutate "magically" in the background but that is the nature of DMA buffers. 
//                 let mut images :   Vec<&'static mut [u16]>  = pyo3::Python::with_gil(|py| {
//                      self.buffers.iter().map(|arr| unsafe {
//                          std::mem::transmute(arr.as_ref(py).as_slice_mut().unwrap())
//                      }).collect()
//                 });
//                 let image_size = [self.buffer_size[2],self.buffer_size[1]];
//                 // let n_pixels = image_size[0]*image_size[1];
//                 let n_buffers = self.buffer_size[0];
//                 //todo this can error out differently? 
//                 while rx.try_recv().is_err() {
//                     let now = std::time::Instant::now();
//                     // println!("{:?}", now);
//                     let image_index = self.last_frame_id % n_buffers;
//                     // let mut slice = self.buffers.index_axis_mut(Axis(0), image_index);//[n_pixels*image_index..n_pixels*(image_index+1)];
//                     let phase_offset = (self.last_frame_id % 128) as f64 / 127.0;
//                     for y in 0..image_size[1]{ 
//                         let yf = (y as f64)/((image_size[0]-1) as f64);
//                         for x in 0..image_size[0]{
//                             let xf = (x as f64)/((image_size[0]-1) as f64);
//                             let val = 350.0*(0.5+0.5*((xf+yf+phase_offset)*6.28).sin());
//                             images[image_index][y*image_size[0]+x] = val.max(0.0) as u16;
//                         }
//                     }
//                     pyo3::Python::with_gil(|py| {
//                         self.frame_processor.call1(py, (&self.buffers[image_index],))
//                     }).unwrap();
//                     let time_taken = std::time::Instant::now()-now;
//                     if time_taken < std::time::Duration::from_millis(25) {
//                         std::thread::sleep(std::time::Duration::from_millis(30) - time_taken);
//                     } else {
//                         eprintln!("Took too long making frame {}: took {} ms", self.last_frame_id, time_taken.as_millis());
//                     }
//                     self.last_frame_id += 1; 
//                 }
//                 println!("thread saw stop, stopping!");
//              })
//         }
//     }

    // pub fn get_last_frame(&self) -> Py<PyArray2<u16>> {
    //     let indx = self.last_frame_index();

    // }
// }

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