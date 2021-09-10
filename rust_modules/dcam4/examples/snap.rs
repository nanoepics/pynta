use dcam4::*;
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut cam = Camera::new();
    let pixels = cam.snap();
    println!("{}", pixels.len());
    println!("{:?}", &pixels[..64]);
    println!("{:?}", &pixels[(pixels.len()-33)..]);
    let mut file = File::create("output.bin").unwrap();
    let bytes = unsafe{
        std::slice::from_raw_parts(std::mem::transmute::<&[u16], &[u8]>(pixels).as_ptr(), pixels.len()*2)
    };
    file.write_all(bytes);
}