use pyo3::prelude::*;
// use pyo3::types::PyDict;
// use pyo3::wrap_pymodule;
use pyo3::exceptions;
// use camera_model::{Camera,Frame};
// use camera_model::devices::dummy::{DummyCamera,DummyFrame};
// use numpy::array::PyArray;
// use ndarray::ArrayView;
// use tokio::runtime::Runtime;
// #[pyclass]
// struct PyCam{
//     inner : Option<DummyCamera>,
//     runtime : tokio::runtime::Runtime,
//     running : std::sync::atomic::AtomicBool
// }

#[pyclass(name="Stage")]
struct PyStage {
    dev : mcl_microdrive::Device
}

struct Wrapper<T>(T);

impl<T : std::fmt::Debug> std::convert::From<Wrapper<T>> for PyErr{
    fn from(e: Wrapper<T>) -> PyErr {
        exceptions::PyException::new_err(format!("{:?}",e.0))
    }
}

fn to_py_err<T,  E : std::fmt::Debug>(original : Result<T,E>) -> PyResult<T> {
    original.map_err(|e| PyErr::from(Wrapper(e)))
}

#[pymethods]
impl PyStage {
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(PyStage{
            dev : mcl_microdrive::get_all_devices().pop().ok_or(exceptions::PyValueError::new_err("No free madcitylabs microdrive found. Is another program holding the handle?"))?
        })
    }
    pub fn move_xy(&self, distance : [f64;2], velocity : [f64;2]) ->   PyResult<()> {
        to_py_err(self.dev.move_two_axis((mcl_microdrive::Axis::M2,mcl_microdrive::Axis::M1), (velocity[0], velocity[1]), (distance[0], distance[1])))
    }
    pub fn move_x(&self, distance : f64, velocity : f64) ->   PyResult<()> {
        to_py_err(self.dev.move_single_axis(mcl_microdrive::Axis::M2, velocity, distance))
    }
    pub fn move_y(&self, distance : f64, velocity : f64) ->   PyResult<()> {
        to_py_err(self.dev.move_single_axis(mcl_microdrive::Axis::M1, velocity, distance))
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
    Ok(())
}

// #[pymethods]
// impl PyCam {
//     #[new]
//     pub fn new() -> Self {
//         Self{inner : Some(DummyCamera::new()), runtime : Runtime::new().unwrap(), running: std::sync::atomic::AtomicBool::new(false)}
//     }

//     fn set_exposure(&mut self, exposure : u64){
//         self.inner.as_mut().unwrap().set_exposure(std::time::Duration::from_millis(exposure));
//     }
//     fn get_exposure(&self) -> u128{
//         self.inner.as_ref().unwrap().get_exposure().as_micros()
//     }
//     fn set_region_of_interest(&mut self, x : (usize, usize), y: (usize, usize)){
//         self.inner.as_mut().unwrap().set_region_of_interest(x, y);
//     }
//     fn get_region_of_interest(&self) -> ((usize, usize), (usize, usize)){
//         self.inner.as_ref().unwrap().get_region_of_interest()
//     }
//     fn set_capture_mode(&mut self, mode : &str){
//         let mode = match mode.to_ascii_lowercase().as_str() {
//             "continuous" => camera_model::CaptureMode::Continous,
//             "single" => camera_model::CaptureMode::SingleShot,
//             "burst" => camera_model::CaptureMode::Burst,
//             _ => unreachable!()
//         };
//         self.inner.as_mut().unwrap().set_capture_mode(mode);
//     }
//     fn get_capture_mode(&self) -> &'static str{
//         match self.inner.as_ref().unwrap().get_capture_mode() {
//             camera_model::CaptureMode::Continous => "continuous",
//             camera_model::CaptureMode::SingleShot => "single",
//             camera_model::CaptureMode::Burst => "burst"
//         }
//     }
//     fn snap(&mut self, callback: &PyAny) -> PyResult<()>{
//         if !callback.is_callable() {
//             Err(exceptions::PyValueError::new_err("argument is not callable"))
//         } else {
//             let image = self.inner.as_mut().unwrap().snap();
//             let shape = image.size();
//             let view = ArrayView::from_shape(shape, image.get_data()).unwrap();
//             let gil = pyo3::Python::acquire_gil();
//             //allocates on every callback, we don't want this, ideally just give it to python with the GC calling back to drop via clone etc and __del__.
//             callback.call1((PyArray::from_array(gil.python(), &view),))?;
//             Ok(())
//         }
//     }

//     fn free_run(&mut self, callback: &PyAny) -> PyResult<()> {
//         if !callback.is_callable() {
//             Err(exceptions::PyValueError::new_err("argument is not callable"))
//         } else {
//             let mut stream = self.inner.take().unwrap().into_data_stream();
//             let cb = PyObject::from(callback);
//             self.runtime.spawn(async move{
//                 loop{
//                     let image = stream.get_next_frame().await;
//                     let shape = image.size();
//                     let view = ArrayView::from_shape(shape, image.get_data()).unwrap();
//                     Python::with_gil(|py| {
//                     //allocates on every callback, we don't want this, ideally just give it to python with the GC calling back to drop via clone etc and __del__.
//                         cb.call1(py, (PyArray::from_array(py, &view),)).unwrap();
//                     });
//                 }
//             });
//             Ok(())
//         }
//     }
//     // async fn create_sleepy(&mut self) -> NoNew {
//     //     self.last += 1;
//     //     NoNew{value: self.last}
//     // }
// }