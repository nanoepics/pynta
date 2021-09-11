use pyo3::prelude::*;
use pyo3::exceptions;
use mcl_stagedrive::microdrive;
use dcam4;
use numpy::{PyArray2};

struct Wrapper<T>(T);

impl<T : std::fmt::Debug> std::convert::From<Wrapper<T>> for PyErr{
    fn from(e: Wrapper<T>) -> PyErr {
        exceptions::PyException::new_err(format!("{:?}",e.0))
    }
}

fn to_py_err<T,  E : std::fmt::Debug>(original : Result<T,E>) -> PyResult<T> {
    original.map_err(|e| PyErr::from(Wrapper(e)))
}

#[pyclass(name="Stage")]
struct PyStage {
    dev : microdrive::Device
}

#[pyclass(name="DcamCamera")]
struct DcamCamera {
    dev : dcam4::Camera
}

impl DcamCamera{
    fn new() -> PyResult<Self> {
        Ok(Self{
            dev: dcam4::Camera::new()
        })
    }
}


use std::sync::mpsc;
use std::thread;

#[pyclass(name="DummyCamera")]
struct DummyCamera {
    last_frame : usize,
    join_handle : Option<thread::JoinHandle<()>>,
    stop_signal : Option<mpsc::SyncSender<()>>
}

impl DummyCamera {
    fn new() -> PyResult<Self> {
        Ok(Self {
            last_frame : 0,
            join_handle : None,
            stop_signal: None
        })
    }

    fn fill_buffer(&mut self, buffer : &mut [u16]) {
        assert_eq!(buffer.len(), 2048*2048);
        let phase_offset = (self.last_frame % 128) as f64 / 127.0;
        for x in 0..2048{
            let xf = (x as f64)/2047.0;
            for y in 0..2048{
                let yf = (y as f64)/2047.0;
                let val = 350.0*(0.5+0.5*((xf+yf+phase_offset)*6.28).sin());
                buffer[x*2048+y] = val.max(0.0) as u16;
            }
        }
        self.last_frame += 1;
    }
}

trait PyCamera{
    // fn new() -> PyResult<Self>;
    fn snap_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()>;
    fn stream_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()>;
    fn is_streaming(&self) -> PyResult<bool>;
    fn stop_stream(&mut self) -> PyResult<()>;
    fn get_size(&self) -> PyResult<[usize;2]>;
    fn get_max_size(&self) -> PyResult<[usize;2]>;
}

impl PyCamera for DcamCamera{
    fn snap_into(&mut self, arr : &PyArray2<u16>) -> PyResult<()> {
        to_py_err(self.dev.snap_into(unsafe{arr.as_slice_mut()?}))
    }
    fn stream_into(&mut self, arr : &PyArray2<u16>) -> PyResult<()> {
        //does this buffer live long enough? should we store a copy of it somewhere in our memory to prevent python from GCing it till we're done with it too?
        to_py_err(self.dev.stream_into(unsafe{arr.as_slice_mut()?}))
    }

    fn stop_stream(&mut self) -> PyResult<()> {
        to_py_err(self.dev.stop_stream())
    }
    fn get_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }
    fn get_max_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }

    fn is_streaming(&self) -> PyResult<bool> {
        //check that status is busy
        unimplemented!()
    }
}

impl PyCamera for DummyCamera{
    fn snap_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()> {
        Ok(self.fill_buffer(unsafe{arr.as_slice_mut()?}))
    }
    fn stream_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()> {
        self.stop_stream()?;
        let (tx, rx) = mpsc::sync_channel::<()>(1);
        self.stop_signal = Some(tx);
        //very bad
        let slice : &'static mut [u16] = unsafe{std::mem::transmute(arr.as_slice_mut()?)};
        self.join_handle = Some(std::thread::spawn(move || {
            let mut last_frame = 0;
            while rx.try_recv().is_err() {
                assert_eq!(slice.len(), 2048*2048);
                let phase_offset = (last_frame % 128) as f64 / 127.0;
                for x in 0..2048{
                    let xf = (x as f64)/2047.0;
                    for y in 0..2048{
                        let yf = (y as f64)/2047.0;
                        let val = 350.0*(0.5+0.5*((xf+yf+phase_offset)*6.28).sin());
                        slice[x*2048+y] = val.max(0.0) as u16;
                    }
                }
                last_frame += 1;
                // println!("finished frame {}", last_frame);
                std::thread::sleep(std::time::Duration::from_millis(20));
            }
        }));
        Ok(())
    }
    fn stop_stream(&mut self) -> PyResult<()> {
        if self.join_handle.is_some() {
            self.stop_signal.take()
                .expect("Trying to stop a stream as the joinhandle exists but the stop sigal doesn't exist?")
                .send(()).unwrap();
            self.join_handle.take().unwrap().join().unwrap();
        }
        Ok(())
    }
    fn get_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }
    fn get_max_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }
    fn is_streaming(&self) -> PyResult<bool> {
        Ok(self.join_handle.is_some())
    }
}

#[pyclass]
pub struct Camera{
    device : Box::<dyn PyCamera + Send>
}

#[pymethods]
impl Camera{
    #[new]
    pub fn new(device : &str) -> PyResult<Self> {
        match device.to_lowercase().as_str() {
            "dcam" | "hamamatsu" => {
                Ok(Self{
                    device : Box::new(DcamCamera::new()?) as Box::<dyn PyCamera + Send>,
                })
            },
            "dummy" | "test" => {
                Ok(Self{
                    device : Box::new(DummyCamera::new()?) as Box::<dyn PyCamera + Send>,
                })
            },
            e => {
                Err(exceptions::PyValueError::new_err(
                    format!("No Camera called \"{}\" supported. Please check for typos, whether other programs using the camera right now, or if pynta_drivers was build with the right features.",e)
                ))
            }
        }
    }

    fn snap_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()> {
        self.device.snap_into(arr)
    }
    fn stream_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()> {
        self.device.stream_into(arr)
    }
    fn stop_stream(&mut self) -> PyResult<()> {
        self.device.stop_stream()
    }
    fn get_size(&self) -> PyResult<[usize;2]> {
        self.device.get_size()
    }
    fn get_max_size(&self) -> PyResult<[usize;2]> {
        self.device.get_max_size()
    }
    fn is_streaming(&self) -> PyResult<bool> {
        self.device.is_streaming()
    }
}


#[pymethods]
impl PyStage {
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(PyStage{
            dev : microdrive::get_all_devices().pop().ok_or(exceptions::PyValueError::new_err("No free madcitylabs microdrive found. Is another program holding the handle?"))?
        })
    }
    pub fn move_xy(&self, distance : [f64;2], velocity : [f64;2]) ->   PyResult<()> {
        to_py_err(self.dev.move_two_axis((microdrive::Axis::M2,microdrive::Axis::M1), (velocity[0], velocity[1]), (distance[0], distance[1])))
    }
    pub fn move_x(&self, distance : f64, velocity : f64) ->   PyResult<()> {
        to_py_err(self.dev.move_single_axis(microdrive::Axis::M2, velocity, distance))
    }
    pub fn move_y(&self, distance : f64, velocity : f64) ->   PyResult<()> {
        to_py_err(self.dev.move_single_axis(microdrive::Axis::M1, velocity, distance))
    }
    pub fn supported_velocity_range(&mut self) -> PyResult<[f64;2]> {
        let info = to_py_err(self.dev.get_info())?;
        let min_velocity = info.min_velocity();
        let max_velocity = *([info.max_velocity_one_axis(), info.max_velocity_two_axis()].iter().min_by(|a, b| b.partial_cmp(a).unwrap()).unwrap());
        Ok([min_velocity, max_velocity])
    }
}

#[pymodule]
fn _pynta_drivers(py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(double, m)?)?;
    m.add_class::<PyStage>()?;
    m.add_class::<Camera>()?;
    Ok(())
}
