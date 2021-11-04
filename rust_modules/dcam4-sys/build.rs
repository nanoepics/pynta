extern crate bindgen;

use std::env;
use std::path::PathBuf;
use std::fs;

fn main() {
    // Tell cargo to look in this folder for the lib files
    let link_dir = PathBuf::from("./sdk/lib/win64");
    println!("cargo:rustc-link-search={}", fs::canonicalize(&link_dir).unwrap().display().to_string());
    // and lick against the dcamapi
    println!("cargo:rustc-link-lib=dcamapi");

    // Tell cargo to invalidate the built crate whenever the wrapper changes
    println!("cargo:rerun-if-changed=wrapper.h");

    // The bindgen::Builder is the main entry point
    // to bindgen, and lets you build up options for
    // the resulting bindings.
    let bindings = bindgen::Builder::default()
        // The input header we would like to generate
        // bindings for.
        .header("wrapper.h")
        // Tell cargo to invalidate the built crate whenever any of the
        // included header files changed.
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        // Finish the builder and generate the bindings.
        .generate()
        // Unwrap the Result and panic on failure.
        .expect("Unable to generate bindings");

    // Write the bindings to the $OUT_DIR/bindings.rs file.
    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .expect("Couldn't write bindings!");
}
