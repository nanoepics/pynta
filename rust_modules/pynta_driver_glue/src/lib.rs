use pyo3::prelude::*;
use pyo3::exceptions;
use mcl_stagedrive::microdrive;
#[pyclass(name="Stage")]
struct PyStage {
    dev : microdrive::Device
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
    Ok(())
}
