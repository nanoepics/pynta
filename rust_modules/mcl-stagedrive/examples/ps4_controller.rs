#[derive(Copy, Clone,Debug,PartialEq)]
#[repr(u16)]
enum PS4ButtonFlags {
    DPadN       = 0x0000,
    DPadNE      = 0x0001,
    DPadE       = 0x0002,
    DPadSE      = 0x0003,
    DPadS       = 0x0004,
    DPadSW      = 0x0005,
    DPadW       = 0x0006,
    DPadNW      = 0x0007,
    DPadNone    = 0x0008,
    DPadMask    = 0x000F,
    Share       = 0x0010,
    Options     = 0x0020,
    Home        = 0x0040,
    L1          = 0x0100,
    R1          = 0x0200,
    L2          = 0x0400,
    R2          = 0x0800,
    Square      = 0x1000,
    Cross       = 0x2000,
    Circle      = 0x4000,
    Triangle    = 0x8000,
}

#[repr(packed)]
#[derive(Copy, Clone,Debug)]
struct PS4Input {
    header: u8,
    left_stick_x: u8,
    left_stick_y: u8,
    right_stick_x: u8,
    right_stick_y: u8,
    buttons: PS4ButtonFlags,
    something: u8,
    l2: u8,
    r2: u8,
}

impl PS4Input {
    fn new(data: [u8; std::mem::size_of::<PS4Input>()]) -> PS4Input {
        unsafe {
            std::mem::transmute(data)
        }
    }
}

fn main() {
    let api = hidapi::HidApi::new().unwrap();
    // Print out information about all connected devices
    // for device in api.devices() {
    //     println!("{:?}", device);
    // }

    println!("Opening...");
    // Connect to device using its VID and PID (Ruyi controller)
    let (VID, PID) = (1356,2508);
    let device = api.open(VID, PID).unwrap();
    let manufacturer = device.get_manufacturer_string().unwrap();
    let product = device.get_product_string().unwrap();
    println!("Product {:?} Device {:?}", manufacturer, product);
    let mcl = &mcl_stagedrive::microdrive::get_all_devices()[0];
    let mut last_x = 0;
    let mut last_y = 0;
    loop {
        //println!("Reading...");
        // Read data from device
        let mut buf = [0u8; std::mem::size_of::<PS4Input>()];
        let res = device.read_timeout(&mut buf[..], 1000).unwrap();
        let inpt = PS4Input::new(buf);
        // println!("Read: {:?}",inpt);
        if inpt.buttons != PS4ButtonFlags::DPadNone {
            return;
        }
        if ((inpt.right_stick_x as i32 -last_x).abs() > 3) || ((inpt.right_stick_y as i32 -last_y).abs() > 3) {
            let x = ((inpt.right_stick_x as f64) - 128.0)/180.0;
            let y = ((inpt.right_stick_y as f64) - 128.0)/180.0;
            let velocities = (if x.abs() > 0.04 { x.abs() } else {0.00}, if y.abs() > 0.04 { y.abs() } else {0.00});
            let distances =  (if x.abs() > 0.04 { (10.0f64).copysign(x) } else {0.0},  if y.abs() > 0.04 { (10.0f64).copysign(y)} else {0.0});
            
            mcl.stop().unwrap();
            if x.hypot(y) > 0.1{
                println!("velocities: {:?}, distances {:?}", velocities, distances);
                mcl.move_two_axis((mcl_stagedrive::microdrive::Axis::M1,mcl_stagedrive::microdrive::Axis::M2), velocities, distances).unwrap();
            } else {
                println!("deadzone");
            }
            last_x = inpt.right_stick_x as i32;
            last_y = inpt.right_stick_y as i32;
        }
        // std::thread::sleep(std::time::Duration::from_millis(20));
    }
}