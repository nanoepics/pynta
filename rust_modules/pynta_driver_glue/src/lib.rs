#![feature(asm)]
use pyo3::prelude::*;
use pyo3::exceptions;
use mcl_stagedrive::microdrive;

use numpy::{PyArray2};

pub mod dummy_camera;
pub use dummy_camera::DummyCamera;

pub mod dcam;
pub use dcam::DcamCamera;

pub(crate) struct Wrapper<T>(T);

impl<T : std::fmt::Debug> std::convert::From<Wrapper<T>> for PyErr{
    fn from(e: Wrapper<T>) -> PyErr {
        exceptions::PyException::new_err(format!("{:?}",e.0))
    }
}

pub(crate) fn to_py_err<T,  E : std::fmt::Debug>(original : Result<T,E>) -> PyResult<T> {
    original.map_err(|e| PyErr::from(Wrapper(e)))
}

#[pyclass(name="Stage")]
struct PyStage {
    dev : microdrive::Device
}


trait PyCamera{
    // fn new() -> PyResult<Self>;
    fn snap_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()>;
    // fn stream_into(&mut self, arr: &mut [u16]) -> PyResult<()>;
    // fn snap(&mut self) -> PyResult<Py<PyArray2<u16>>
    fn is_streaming(&self) -> PyResult<bool>;
    fn start_stream(&mut self, n_buffers : usize, callable : PyObject) -> PyResult<()>;
    fn stop_stream(&mut self) -> PyResult<()>;
    fn get_size(&self) -> PyResult<[usize;2]>{
        let roi = self.get_roi()?;
        Ok([roi.0[1]-roi.0[0], roi.1[1]-roi.1[0]])
    }
    fn get_max_size(&self) -> PyResult<[usize;2]>;
    fn set_roi(&mut self, x : [usize;2], y : [usize;2]) -> PyResult<([usize;2], [usize;2])>;
    fn get_roi(&self) -> PyResult<([usize;2], [usize;2])>;
    fn set_exposure(&mut self, exposure_in_seconds: f64) -> PyResult<f64>;
    fn get_exposure(&self) -> PyResult<f64>;
}

impl PyCamera for DummyCamera{
    fn snap_into(&mut self, arr: &PyArray2<u16>) -> PyResult<()> {
        Ok(self.fill_buffer(unsafe{arr.as_slice_mut()?}))
    }
    // fn stream_into(&mut self, arr: &mut [u16]) -> PyResult<()> {
    // }
    fn start_stream(&mut self, n_buffers : usize, callable : PyObject) -> PyResult<()>{
        // let stream_generator = dummy_camera::CameraStreamer::new(callable, n_buffers, self.get_size())?;
        // self.streamer = Some(stream_generator.start());
        // Ok(())
        self.start_stream(n_buffers, callable)
    }

    fn stop_stream(&mut self) -> PyResult<()> {
        if self.streamer.is_some(){
            // println!("iissueing a stop on reactor");
            self.streamer.take().unwrap().stop();
            println!("stopped");
        }
        Ok(())
    }
    fn get_roi(&self) -> PyResult<([usize;2], [usize;2])> {
        Ok(self.get_roi())
    }
    fn set_roi(&mut self, x: [usize;2], y : [usize;2]) -> PyResult<([usize;2], [usize;2])> {
        let max = self.get_max_size()?;
        self.roi = ([(x[0].min(x[1])), (x[0].max(x[1])).min(max[0])], [(y[0].min(y[1])), (y[0].max(y[1])).min(max[1])]);
        <Self as PyCamera>::get_roi(&self)
    }
    fn get_max_size(&self) -> PyResult<[usize;2]> {
        Ok([2048, 2048])
    }
    fn is_streaming(&self) -> PyResult<bool> {
        Ok(self.streamer.is_some())
    }
    fn set_exposure(&mut self, exposure_in_seconds: f64) -> PyResult<f64> {
        self.get_exposure()
    }
    fn get_exposure(&self) -> PyResult<f64> {
        Ok(0.0)
    }
}

#[pyclass]
pub struct Camera{
    device : Box::<dyn PyCamera + Send>,
    // buffers : Option<Py<PyArray3<u16>>>
}

#[pymethods]
impl Camera{
    #[new]
    pub fn new(device : &str) -> PyResult<Self> {
        match device.to_lowercase().as_str() {
            "dcam" | "hamamatsu" => {
                Ok(Self{
                    device : Box::new(DcamCamera::new()?) as Box::<dyn PyCamera + Send>,
                    // buffers : None,
                })
            },
            "dummy" | "test" => {
                Ok(Self{
                    device : Box::new(DummyCamera::new()?) as Box::<dyn PyCamera + Send>,
                    // buffers: None,
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
    fn start_stream(&mut self, n_buffers: usize, callable : PyObject, py: Python) -> PyResult<()> {
        py.allow_threads(||{self.device.start_stream(n_buffers, callable)})
    }
    
    fn stop_stream(&mut self, py: Python) -> PyResult<()> {
        println!("trying to stop stream");
        py.allow_threads(||{self.device.stop_stream()})
    }
    fn get_size(&mut self, py: Python) -> PyResult<[usize;2]> {
        py.allow_threads(||{
            let size = {&mut self.device}.get_size()?;
            println!("size is {:?}", size);
            Ok([size[1], size[0]])
        })
    }
    fn get_max_size(&self, py: Python) -> PyResult<[usize;2]> {
        self.device.get_max_size()
    }
    fn set_roi(&mut self, x : [usize;2], y : [usize;2], py: Python) -> PyResult<([usize;2],[usize;2])> {
        py.allow_threads(||{self.device.set_roi(x,y)})
    }
    fn get_roi(&mut self, py: Python) -> PyResult<([usize;2],[usize;2])>{
        py.allow_threads(||{(&mut self.device).get_roi()})
    }
    fn set_exposure(&mut self, exposure_in_seconds: f64, py: Python) -> PyResult<f64> {
        py.allow_threads(||{(&mut self.device).set_exposure(exposure_in_seconds)})
    }
    fn get_exposure(&mut self, py: Python) -> PyResult<f64> {
        py.allow_threads(||(&mut self.device).get_exposure())
    }
    fn is_streaming(&mut self, py: Python) -> PyResult<bool> {
        py.allow_threads(||{&mut self.device}.is_streaming())
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
fn _pynta_drivers(_py: Python, m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(double, m)?)?;
    m.add_class::<PyStage>()?;
    m.add_class::<Camera>()?;
    Ok(())
}
