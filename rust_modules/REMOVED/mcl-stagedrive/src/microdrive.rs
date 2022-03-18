use mcl_microdrive_sys::*;
use crate::*;

use std::convert::{TryInto,From};
use std::os::raw::{c_int,c_short,c_uint, c_ushort, c_uchar, c_double};


#[derive(Debug)]
pub struct DeviceInfo{
    encoder_resolution : c_double,
    step_size : c_double,
    max_velocity_one_axis : c_double,
    max_velocity_two_axis : c_double,
    max_velocity_three_axis : c_double,
    min_velocity : c_double,
}

impl DeviceInfo{
    pub fn encoder_resolution(&self) -> f64 {
        self.encoder_resolution
    }
    pub fn step_size(&self) -> f64 {
        self.step_size
    }
    pub fn max_velocity_one_axis(&self) -> f64 {
        self.max_velocity_one_axis
    }
    pub fn max_velocity_two_axis(&self) -> f64 {
        self.max_velocity_two_axis
    }
    pub fn max_velocity_three_axis(&self) -> f64 {
        self.max_velocity_three_axis
    }
    pub fn min_velocity(&self) -> f64 {
        self.min_velocity
    }
}

#[derive(Debug)]
pub struct Device{
    handle: c_int,
    info : Option<DeviceInfo>,
}

#[derive(Debug,Copy,Clone)]
pub struct ProductId(c_ushort);

#[repr(u16)]
pub enum Products{
    MicroDrive6,
    MicroDrive4,
    MicroDrive3,
    MicroDrive,
    NanoCyteMicroDrive,
    MicroDrive1,
    Unknown(u16)
}

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

#[derive(Debug)]
#[repr(u32)]
pub enum Axis{
    NoAxis = 0,
    M1 = 1,
    M2 = 2,
    M3 = 3,
    M4 = 4,
    M5 = 5,
    M6 = 6
}

impl Device {
    pub fn new_fake(handle : c_int) -> Self {
        Self{handle, info : None}
    }
    pub fn firmware_version(&self) -> Result<FirmwareVersion, Errors> {
        let mut firmware = FirmwareVersion{ version :0, profile : 0};
        error_or(unsafe{DLL.MCL_GetFirmwareVersion(&mut firmware.version, &mut firmware.profile, self.handle)}, firmware)
    }

    //NOTE: the documentation does not this function can return an error, but it can. 
    pub fn serial_number(&self) -> Result<SerialNumber, Errors> {
        let serial = SerialNumber(unsafe{DLL.MCL_GetSerialNumber(self.handle)});
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
            Ok(unsafe{DLL.MCL_DeviceAttached(time_to_wait_milis, self.handle)})
        }
    }

    // pub async fn wait_attached(self) -> Self{
    //     loop{
    //         if unsafe{DLL.MCL_DeviceAttached(0, self.handle)} {
    //             return self
    //         }
    //     }
    // }

    pub fn product_id(&self) -> Result<ProductId,Errors> {
        let mut ret = ProductId(0);
        error_or(unsafe{DLL.MCL_GetProductID(&mut ret.0, self.handle)}, ret)
    }

    pub fn axis_info(&self) -> Result<AxisInfo, Errors> {
        let mut ret = AxisInfo{bitmap : 0};
        error_or(unsafe{DLL.MCL_GetAxisInfo(&mut ret.bitmap, self.handle)}, ret)
    }
    //units?
    pub fn full_step_size(&self) -> Result<f64, Errors> {
        let mut ret = 0.0;
        error_or(unsafe{DLL.MCL_GetFullStepSize(&mut ret, self.handle)}, ret)
    }
    
    pub fn tirf_module_callibration_in_mm(&self) -> Result<f64, Errors> {
        let mut ret = 0.0;
        error_or(unsafe{DLL.MCL_GetTirfModuleCalibration(&mut ret, self.handle)}, ret)
    }

    pub fn wait_for_move_to_finish(&self) -> Result<(), Errors> {
        error_or(unsafe{DLL.MCL_MicroDriveWait(self.handle)}, ())
    }

    pub fn move_single_axis(&self, axis: Axis, velocity_in_mm_per_s :  f64, distance_in_mm : f64) -> Result<(),Errors>{
        error_or(unsafe{DLL.MCL_MDMove(axis as c_uint, velocity_in_mm_per_s, distance_in_mm, self.handle)}, ())
    }

    pub fn move_two_axis(&self, axis: (Axis, Axis), velocity_in_mm_per_s :  (f64,f64), distance_in_mm : (f64,f64)) -> Result<(),Errors>{
        self.move_three_axis( (axis.0, axis.1, Axis::NoAxis), (velocity_in_mm_per_s.0, velocity_in_mm_per_s.1, 0.0), (distance_in_mm.0, distance_in_mm.1, 0.0))
    }

    //TODO: might be more of a 'queue move'
    pub fn move_three_axis(&self, axis: (Axis, Axis, Axis), velocity_in_mm_per_s :  (f64,f64,f64), distance_in_mm : (f64,f64,f64)) -> Result<(),Errors>{
        error_or(unsafe{DLL.MCL_MDMoveThreeAxes(
            axis.0 as c_int, velocity_in_mm_per_s.0, distance_in_mm.0,
            axis.1 as c_int, velocity_in_mm_per_s.1, distance_in_mm.1,
            axis.2 as c_int, velocity_in_mm_per_s.2, distance_in_mm.2,
            self.handle
        )}, ())
    }

    pub fn get_info(&mut self) -> Result<&DeviceInfo, Errors> {
        if self.info.is_some() {
            Ok(self.info.as_ref().unwrap())
        } else {
            let mut info = DeviceInfo{encoder_resolution : 0.0, step_size : 0.0, max_velocity_one_axis : 0.0, max_velocity_two_axis :0.0, max_velocity_three_axis : 0.0, min_velocity : 0.0};
            let possible_error = unsafe{ DLL.MCL_MDInformation(&mut info.encoder_resolution, &mut info.step_size, &mut info.max_velocity_one_axis, &mut info.max_velocity_two_axis, &mut info.max_velocity_three_axis, &mut info.min_velocity, self.handle)};
            Result::<(),Errors>::from(Errors::from(possible_error)).map(move |_| {
                self.info = Some(info);
                self.info.as_ref().unwrap()
            })
        }
    }

    pub fn stop(&self) -> Result<(), Errors> {
        let mut _status = 0;
        error_or(unsafe{ DLL.MCL_MDStop(&mut _status, self.handle) }, ())
    }

}

impl std::ops::Drop for Device {
    fn drop(&mut self){
        unsafe{
            let mut _status = 0;
            //attempt to issue a stop command to the device before releasing the handle, as a safeguard to stop the stage from moving if the program crashes (assuming it still manages to drop the Device)
            //this can fail, in which case an error handling mechanism like https://github.com/diesel-rs/diesel/blob/036985ed2c2d2ac1b927f810b89af54d5852826d/diesel/src/sqlite/connection/stmt.rs#L156-L170 would be nice
            DLL.MCL_MDStop(&mut _status, self.handle);
            DLL.MCL_ReleaseHandle(self.handle);
        }
    }
}

pub fn get_all_devices() -> Vec<Device>{
    let n_devices = unsafe{DLL.MCL_GrabAllHandles()};
    let mut devices = vec![0;n_devices.try_into().unwrap()];
    assert_eq!(n_devices, unsafe{DLL.MCL_GetAllHandles(devices.as_mut_ptr(), devices.len() as c_int)});
    devices.into_iter().map(|handle| Device {handle, info : None}).collect()
}



pub fn get_dll_version() -> DllVersion {
    let mut ret = DllVersion{version: 0, revision:0};
    unsafe{DLL.MCL_DLLVersion(&mut ret.version, &mut ret.revision);}
    ret
}

pub fn correct_driver_version() -> bool{
    unsafe{DLL.MCL_CorrectDriverVersion()}
}

pub fn check_dll() -> Result<DllVersion, DllVersion> {
    match correct_driver_version() {
        true => Ok(get_dll_version()),
        false => Err(get_dll_version())
    }
}
