use mcl_microdrive_sys::*;
use std::convert::{TryInto,From};
use std::os::raw::{c_int,c_short,c_double, c_ushort, c_uchar};
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

fn error_or<T, E : Into<Errors>>(error : E, value : T) -> Result<T, Errors>{
    Result::<(),Errors>::from(error.into()).map(|_| value)
}
#[derive(Debug, Default)]
pub struct Device{
    handle: c_int
}

#[derive(Debug,Copy,Clone)]
pub struct FirmwareVersion{
    version : c_short,
    profile : c_short
}

impl FirmwareVersion{
    pub fn version(&self) -> i32{
        self.version as i32
    }

    pub fn profile(&self) -> i32{
        self.profile as i32
    }
}

#[derive(Debug,Copy,Clone)]
pub struct SerialNumber(c_int);

#[derive(Debug,Copy,Clone)]
pub struct ProductId(c_ushort);

#[derive(Debug,Copy,Clone)]
pub struct AxisInfo{
    bitmap : c_uchar,
}

impl AxisInfo{
    pub fn axis_is_available(&self, axis : u8) -> Result<bool,Errors> {
        if (axis > 6) | (axis < 1) {
            Err(Errors::ArgumentError)
        } else {
            Ok( (self.bitmap & (1 << (axis-1))) != 0)
        }
    }
    #[allow(non_snake_case)]
    pub fn axis_M1_is_available(&self) -> bool {
        self.axis_is_available(1).unwrap()
    }
    #[allow(non_snake_case)]
    pub fn axis_M2_is_available(&self) -> bool {
        self.axis_is_available(2).unwrap()
    }
    #[allow(non_snake_case)]
    pub fn axis_M3_is_available(&self) -> bool {
        self.axis_is_available(3).unwrap()
    }
    #[allow(non_snake_case)]
    pub fn axis_M4_is_available(&self) -> bool {
        self.axis_is_available(4).unwrap()
    }
    #[allow(non_snake_case)]
    pub fn axis_M5_is_available(&self) -> bool {
        self.axis_is_available(5).unwrap()
    }
    #[allow(non_snake_case)]
    pub fn axis_M6_is_available(&self) -> bool {
        self.axis_is_available(6).unwrap()
    }
}

impl Device {
    pub fn new_fake(handle : c_int) -> Self {
        Self{handle}
    }
    pub fn firmware_version(&self) -> Result<FirmwareVersion, Errors> {
        let mut firmware = FirmwareVersion{ version :0, profile : 0};
        error_or(unsafe{MCL_GetFirmwareVersion(&mut firmware.version, &mut firmware.profile, self.handle)}, firmware)
    }

    //NOTE: the documentation does not this function can return an error, but it can. 
    pub fn serial_number(&self) -> Result<SerialNumber, Errors> {
        let serial = SerialNumber(unsafe{MCL_GetSerialNumber(self.handle)});
        match serial.0 {
            x if x < 0 => Err(x.into()),
            _ => Ok(serial)
        }
    }

    pub fn is_attached(&self, time_to_wait : std::time::Duration) -> Result<bool, Errors> {
        let time_to_wait_milis = time_to_wait.as_millis();
        if time_to_wait_milis > c_int::MAX as u128{
            Err(Errors::ArgumentError)
        } else {
            let time_to_wait_milis = time_to_wait_milis as c_int;
            //NOTE: time is listed as unsigned int in the docs but int in the header files
            Ok(unsafe{MCL_DeviceAttached(time_to_wait_milis, self.handle)})
        }
    }

    // pub async fn wait_attached(self) -> Self{
    //     loop{
    //         if unsafe{MCL_DeviceAttached(0, self.handle)} {
    //             return self
    //         }
    //     }
    // }

    pub fn product_id(&self) -> Result<ProductId,Errors> {
        let mut ret = ProductId(0);
        error_or(unsafe{MCL_GetProductID(&mut ret.0, self.handle)}, ret)
    }

    pub fn axis_info(&self) -> Result<AxisInfo, Errors> {
        let mut ret = AxisInfo{bitmap : 0};
        error_or(unsafe{MCL_GetAxisInfo(&mut ret.bitmap, self.handle)}, ret)
    }
    //units?
    pub fn full_step_size(&self) -> Result<f64, Errors> {
        let mut ret = 0.0;
        error_or(unsafe{MCL_GetFullStepSize(&mut ret, self.handle)}, ret)
    }
    
    pub fn tirf_module_callibration_in_mm(&self) -> Result<f64, Errors> {
        let mut ret = 0.0;
        error_or(unsafe{MCL_GetTirfModuleCalibration(&mut ret, self.handle)}, ret)
    }

    pub fn wait_for_move_to_finish(&self) -> Result<(), Errors> {
        error_or(unsafe{MCL_MicroDriveWait(self.handle)}, ())
    }

}

impl std::ops::Drop for Device {
    fn drop(&mut self){
        unsafe{MCL_ReleaseHandle(self.handle)}
    }
}

pub fn get_all_devices() -> Vec<Device>{
    let n_devices = unsafe{MCL_GrabAllHandles()};
    let mut devices = vec![0;n_devices.try_into().unwrap()];
    assert_eq!(n_devices, unsafe{MCL_GetAllHandles(devices.as_mut_ptr(), devices.len() as c_int)});
    devices.into_iter().map(|handle| Device {handle}).collect()
}

#[derive(Debug, Copy, Clone)]
pub struct DllVersion{
    version : c_short,
    revision: c_short
}

impl DllVersion{
    pub fn version(&self) -> i32 {
        self.version as i32
    }
    pub fn revision(&self) -> i32 {
        self.revision as i32
    }
}

pub fn get_dll_version() -> DllVersion {
    let mut ret = DllVersion{version: 0, revision:0};
    unsafe{MCL_DLLVersion(&mut ret.version, &mut ret.revision);}
    ret
}

pub fn correct_driver_version() -> bool{
    unsafe{MCL_CorrectDriverVersion()}
}

pub fn check_dll() -> Result<DllVersion, DllVersion> {
    match correct_driver_version() {
        true => Ok(get_dll_version()),
        false => Err(get_dll_version())
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
