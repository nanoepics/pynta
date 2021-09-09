use std::convert::From;
use std::os::raw::c_int;

#[cfg(feature = "microdrive")]
use mcl_microdrive_sys::*;
#[cfg(all(feature="madlib", not(feature = "microdrive")))]
use mcl_madlib_sys::*;
#[cfg(not(any(feature="madlib", feature = "microdrive")))]
compile_error!("Enable either feature `madlib`, `microdrive` or both/default.");

#[derive(Debug)]
pub enum Errors{
    NoError,
    GeneralError,
    DevError,
    DevNotAttached,
    UsageError,
    DevNotReady,
    ArgumentError,
    InvalidAxis,
    InvalidHandle,
    UnknownError(i64)
}

impl From<c_int> for Errors{
    fn from(value: c_int) -> Self {
        match value {
            0 => Errors::NoError,
            MCL_GENERAL_ERROR => Errors::GeneralError,
            MCL_DEV_ERROR => Errors::DevError,
            MCL_DEV_NOT_ATTACHED => Errors::DevNotAttached,
            MCL_USAGE_ERROR => Errors::UsageError,
            MCL_DEV_NOT_READY => Errors::DevNotReady,
            MCL_ARGUMENT_ERROR => Errors::ArgumentError,
            MCL_INVALID_AXIS => Errors::InvalidAxis,
            MCL_INVALID_HANDLE => Errors::InvalidHandle,
            x => Errors::UnknownError(x as i64),
        }
    }
}

impl From<Errors> for Result<(),Errors>{
    fn from(value: Errors) -> Self {
        match value {
            Errors::NoError => Ok(()),
            e => Err(e),
        }
    }
}

pub(crate) fn error_or<T, E : Into<Errors>>(error : E, value : T) -> Result<T, Errors>{
    Result::<(),Errors>::from(error.into()).map(|_| value)
}