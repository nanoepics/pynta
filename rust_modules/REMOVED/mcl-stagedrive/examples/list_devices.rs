fn main() {
    let dll_version = mcl_stagedrive::microdrive::get_dll_version();
    println!("microdrive {:?} -> version {}, revsion {}", dll_version, dll_version.version(), dll_version.revision());
    println!("corrrect driver version: {}", mcl_stagedrive::microdrive::correct_driver_version());
    let devices = mcl_stagedrive::microdrive::get_all_devices();
    println!("found {} micro devices", devices.len());
    for mut dev in devices {
        println!("Device {:?}", dev);
        println!("\tfirmware version: {:?}", dev.firmware_version());
        println!("\tserial number: {:?}", dev.serial_number());
        println!("\tattached? {:?}", dev.is_attached(std::time::Duration::from_millis(0)));
        println!("\tproduct id: {:?}", dev.product_id());
        println!("\tfull step size: {:?}", dev.full_step_size());
        println!("\tTIRF calibration (mm): {:?}", dev.tirf_module_callibration_in_mm());
        let axis = dev.axis_info();
        println!("\taxis info: {:?}", axis);
        if axis.is_ok() {
            let axis = axis.unwrap();
            for i in 1..=6 {
                println!("\t\tAxis {} is available? {}", i, axis.axis_is_available(i as u8).unwrap());
            }
        }
        println!("\tInfo: {:?}", dev.get_info())
    }

    let dll_version = mcl_stagedrive::madlib::get_dll_version();
    println!("madlib {:?} -> version {}, revsion {}", dll_version, dll_version.version(), dll_version.revision());
    println!("corrrect driver version: {}", mcl_stagedrive::madlib::correct_driver_version());
    let devices = mcl_stagedrive::madlib::get_all_devices();
    println!("found {} nano devices", devices.len());
    for mut dev in devices {
        println!("Device {:?}", dev);
        println!("\tfirmware version: {:?}", dev.firmware_version());
        println!("\tserial number: {:?}", dev.serial_number());
        println!("\tattached? {:?}", dev.is_attached(std::time::Duration::from_millis(0)));
        println!("\tproduct id: {:?}", dev.product_id());
        // println!("\tfull step size: {:?}", dev.full_step_size());
        // println!("\tTIRF calibration (mm): {:?}", dev.tirf_module_callibration_in_mm());
        let axis = dev.axis_info();
        println!("\taxis info: {:?}", axis);
        if axis.is_ok() {
            let axis = axis.unwrap();
            for i in 0..=4 {
                println!("\t\tAxis {} is available? {}", i, axis.axis_is_available(i as u8).unwrap());
            }
        }
        // println!("\tInfo: {:?}", dev.get_info())
    }
}