fn main() {
    let dll_version = mcl_microdrive::get_dll_version();
    println!("{:?} -> version {}, revsion {}", dll_version, dll_version.version(), dll_version.revision());
    println!("corrrect driver version: {}", mcl_microdrive::correct_driver_version());
    let devices = mcl_microdrive::get_all_devices();
    println!("found {} devices", devices.len());
    for dev in devices {
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
    }

    let dev = mcl_microdrive::Device::new_fake(0);
    println!("firmware version: {:?}", dev.firmware_version());
    println!("serial number: {:?}", dev.serial_number());
    println!("attached? {:?}", dev.is_attached(std::time::Duration::from_millis(0)));
    println!("product id: {:?}", dev.product_id());
    println!("full step size: {:?}", dev.full_step_size());
    println!("TIRF calibration (mm): {:?}", dev.tirf_module_callibration_in_mm());
    let axis = dev.axis_info();
    println!("axis info: {:?}", axis);
    if axis.is_ok() {
        let axis = axis.unwrap();
        for i in 1..=6 {
            println!("Axis {} is available? {}", i, axis.axis_is_available(i as u8).unwrap());
        }
    }
}