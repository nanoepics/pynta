#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]

include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
lazy_static::lazy_static!{
    pub static ref DLL: Madlib = unsafe{Madlib::new(libloading::library_filename("Madlib")).expect("Couldn't load the Madlib shared library!")};
}