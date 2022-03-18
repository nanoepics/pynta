use mcl_madlib_sys::*;
use crate::*;

use std::convert::{TryInto};
use std::os::raw::{c_int, c_ushort, c_uchar};

#[derive(Debug,Copy,Clone)]
pub struct AxisInfo{
    bitmap : c_uchar,
}

impl AxisInfo{
    unsafe fn axis_is_available_unchecked(&self, axis : u8) -> bool {
            (self.bitmap & (1 << axis)) != 0
    }
    pub fn axis_is_available(&self, axis : u8) -> Result<bool,Errors> {
        if axis > 4 {
            Err(Errors::ArgumentError)
        } else {
            Ok(unsafe{self.axis_is_available_unchecked(axis)})
        }
    }
    pub fn x_axis_available(&self) -> bool {
        unsafe{self.axis_is_available_unchecked(0)}
    }
    pub fn y_axis_available(&self) -> bool {
        unsafe{self.axis_is_available_unchecked(1)}
    }
    pub fn z_axis_available(&self) -> bool {
        unsafe{self.axis_is_available_unchecked(2)}
    }
    pub fn aux_axis_available(&self) -> bool {
        unsafe{self.axis_is_available_unchecked(3)}
    }
    pub fn z_encoder_available(&self) -> bool {
        unsafe{self.axis_is_available_unchecked(4)}
    }
}

pub struct DeviceInfo{
    c_inner : ProductInformation
}

impl DeviceInfo{
    pub fn axis_info(&self) -> AxisInfo {
        AxisInfo{bitmap : self.c_inner.axis_bitmap}
    }
    pub fn adc_resolution(&self) -> i32 {
        self.c_inner.ADC_resolution as i32
    }
    pub fn dac_resolution(&self) -> i32 {
        self.c_inner.DAC_resolution as i32
    }
    pub fn product_id(&self) -> ProductId {
        ProductId(self.c_inner.Product_id as c_ushort)
    }
    pub fn firmware_version(&self) -> FirmwareVersion {
        FirmwareVersion{version : self.c_inner.FirmwareVersion, profile: self.c_inner.FirmwareProfile}
    }
}

#[derive(Debug)]
pub struct Device{
    handle: c_int,
}

// pub enum Products{
//     0x2001 Nano-Drive Single Axis
// 		0x2003 Nano-Drive Three Axis
// 		0x2053 Nano-Drive 16 bit Tip/Tilt Z
// 		0x2004 Nano-Drive Four Axis
// 		0x2201 Nano-Drive 20 bit Single Axis
// 		0x2203 Nano-Drive 20 bit Three Axis
// 		0x2253 Nano-Drive 20 bit Tip/Tilt Z
// 		0x2100 Nano-Gauge
// 		0x2401 C-Focus
// }

impl Device {
    pub fn new_fake(handle : c_int) -> Self {
        Self{handle}
    }
    pub fn firmware_version(&self) -> Result<FirmwareVersion, Errors> {
        let mut firmware = FirmwareVersion{ version :0, profile : 0};
        error_or(unsafe{DLL.MCL_GetFirmwareVersion(&mut firmware.version, &mut firmware.profile, self.handle)}, firmware)
    }

    pub fn product_id(&self) -> Result<ProductId,Errors> {
        Ok(self.get_info()?.product_id())
    }

    pub fn axis_info(&self) -> Result<AxisInfo, Errors> {
        Ok(self.get_info()?.axis_info())
    }

    pub fn adc_resolution(&self) -> Result<i32, Errors> {
        Ok(self.get_info()?.adc_resolution())   
    }

    pub fn dac_resolution(&self) -> Result<i32, Errors> {
        Ok(self.get_info()?.dac_resolution())   
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

    pub fn get_info(&self) -> Result<DeviceInfo,Errors> {
        let mut info = DeviceInfo{c_inner : ProductInformation{axis_bitmap : 0, ADC_resolution :0, DAC_resolution : 0, Product_id : 0, FirmwareVersion: 0, FirmwareProfile : 0}};
        error_or(unsafe{DLL.MCL_GetProductInfo(&mut info.c_inner, self.handle)}, info)
    }

    pub fn move_to_z(&self, position_in_microns : f64) -> Result<(),Errors> {
        error_or(unsafe{DLL.MCL_SingleWriteZ(position_in_microns, self.handle)}, ())
    }
    pub fn read_position_z(&self) -> Result<f64, Errors> {
        let ret : f64 = unsafe{DLL.MCL_SingleReadZ(self.handle)};
        if ret < 0.0 {
            //what in tarnation...  
            Err(Errors::from(ret as c_int))
        } else {
            Ok(ret)
        }
    }
}

impl std::ops::Drop for Device {
    fn drop(&mut self){
        unsafe{
            let mut _status = 0;
            DLL.MCL_ReleaseHandle(self.handle);
        }
    }
}

pub fn get_all_devices() -> Vec<Device>{
    let n_devices = unsafe{DLL.MCL_GrabAllHandles()};
    let mut devices = vec![0;n_devices.try_into().unwrap()];
    assert_eq!(n_devices, unsafe{DLL.MCL_GetAllHandles(devices.as_mut_ptr(), devices.len() as c_int)});
    devices.into_iter().map(|handle| Device {handle}).collect()
}

pub fn get_dll_version() -> DllVersion {
    let mut ret = DllVersion{version: 0, revision:0};
    unsafe{DLL.MCL_DLLVersion(&mut ret.version, &mut ret.revision);}
    ret
}

pub fn correct_driver_version() -> bool{
    unsafe{DLL.MCL_CorrectDriverVersion()}
}