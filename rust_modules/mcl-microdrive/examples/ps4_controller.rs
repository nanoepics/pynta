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
    let mcl = &mcl_microdrive::get_all_devices()[0];
    loop {
        println!("Reading...");
        // Read data from device
        let mut buf = [0u8; std::mem::size_of::<PS4Input>()];
        let res = device.read_timeout(&mut buf[..], 1000).unwrap();
        let inpt = PS4Input::new(buf);
        println!("Read: {:?}",inpt);
        if inpt.buttons != PS4ButtonFlags::DPadNone {
            return;
        }
        let x = ((inpt.right_stick_x as f64) - 128.0)/255.0;
        let y = ((inpt.right_stick_x as f64) - 128.0)/255.0;
        mcl.stop().unwrap();
        mcl.move_two_axis((mcl_microdrive::Axis::M1,mcl_microdrive::Axis::M2), (x.abs(), y.abs()), ((1.0f64).copysign(x), (1.0f64).copysign(y))).unwrap();
        //thread::sleep(Duration::from_secs(1));
    }
}