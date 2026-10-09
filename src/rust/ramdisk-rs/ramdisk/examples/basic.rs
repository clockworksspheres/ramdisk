//! Basic usage example.
//!
//!   cargo run --example basic
//!
//! By default this creates a ramdisk, writes a file, then **leaves it mounted**
//! when the process exits (via `detach()`). Pass `--umount` to clean up.

use std::env;
use std::fs;
use std::io::Write;

use ramdisk::{RamDisk, RamDiskOptions};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let do_umount = env::args().any(|a| a == "--umount");

    let opts = RamDiskOptions {
        size_mb: 256,
        ..Default::default()
    };

    println!("Creating 256 MiB ramdisk…");
    let rd = RamDisk::new(opts)?;

    let info = rd.get_data();
    println!("  success     = {}", info.success);
    println!("  mount_point = {}", info.mount_point.display());
    println!("  device      = {:?}", info.device);
    println!("  version     = {}", rd.version());

    // Write a test file
    let test_file = info.mount_point.join("hello.txt");
    {
        let mut f = fs::File::create(&test_file)?;
        writeln!(f, "Hello from a Rust ramdisk!")?;
    }
    println!("Wrote {}", test_file.display());

    let contents = fs::read_to_string(&test_file)?;
    println!("Read back: {}", contents.trim());

    if do_umount {
        println!("Unmounting…");
        rd.umount()?;
        println!("Done.");
    } else {
        let info = rd.detach();
        println!();
        println!("Ramdisk left mounted at {}", info.mount_point.display());
        println!("Unmount later with:  ramdisk umount {}", info.mount_point.display());
        println!("(or re-run this example with --umount)");
    }

    Ok(())
}
