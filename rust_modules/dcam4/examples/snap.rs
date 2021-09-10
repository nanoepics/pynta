use dcam4::*;

fn main() {
    let mut cam = Camera::new();
    let pixels = cam.snap();
    println!("{:?}", pixels);
}