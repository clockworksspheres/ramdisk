//! Command-line interface for the ramdisk library.
//!
//! Usage:
//!   ramdisk create [--size <MiB>] [--mount <path>] [--keep]
//!   ramdisk list
//!   ramdisk umount <mount-or-device>
//!   ramdisk info
//!   ramdisk help

use std::env;
use std::io::{self, Write};
use std::path::PathBuf;
use std::process;

use ramdisk::{list_mounted, umount_path, RamDisk, RamDiskOptions};

fn main() {
    if let Err(e) = run() {
        eprintln!("error: {}", e);
        process::exit(1);
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = env::args().skip(1).collect::<Vec<_>>();

    if args.is_empty() {
        print_help();
        return Ok(());
    }

    let cmd = args.remove(0).to_lowercase();
    match cmd.as_str() {
        "create" | "c" => cmd_create(&args)?,
        "list" | "ls" | "l" => cmd_list()?,
        "umount" | "unmount" | "eject" | "u" => cmd_umount(&args)?,
        "info" | "i" => cmd_info()?,
        "help" | "-h" | "--help" => print_help(),
        "version" | "-V" | "--version" => {
            println!("ramdisk {}", env!("CARGO_PKG_VERSION"));
        }
        other => {
            eprintln!("unknown command: {}", other);
            print_help();
            process::exit(2);
        }
    }
    Ok(())
}

fn print_help() {
    println!(
        r#"ramdisk {} – cross-platform ramdisk tool

USAGE:
    ramdisk <COMMAND> [OPTIONS]

COMMANDS:
    create, c              Create and mount a ramdisk
    list, ls, l            List currently mounted ramdisks
    umount, unmount, u     Unmount a ramdisk by mount point or device
    info, i                Show platform / version information
    help, -h, --help       Show this help
    version, -V            Show version

CREATE OPTIONS:
    --size, -s <MiB>       Size in mebibytes (default: 512)
    --mount, -m <path>     Explicit mount point (default: temp directory)
    --keep, -k             Keep the process running until Enter is pressed
                           (otherwise the ramdisk is unmounted on exit)

EXAMPLES:
    ramdisk create --size 1024
    ramdisk create -s 256 -m /mnt/buildcache --keep
    ramdisk list
    ramdisk umount /mnt/buildcache
"#,
        env!("CARGO_PKG_VERSION")
    );
}

fn cmd_create(args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    let mut size_mb: u64 = 512;
    let mut mount: Option<PathBuf> = None;
    let mut keep = false;

    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--size" | "-s" => {
                i += 1;
                if i >= args.len() {
                    return Err("--size requires a value".into());
                }
                size_mb = args[i]
                    .trim_end_matches(|c: char| matches!(c, 'm' | 'M' | 'b' | 'B'))
                    .parse()
                    .map_err(|_| format!("invalid size: {}", args[i]))?;
            }
            "--mount" | "-m" => {
                i += 1;
                if i >= args.len() {
                    return Err("--mount requires a path".into());
                }
                mount = Some(PathBuf::from(&args[i]));
            }
            "--keep" | "-k" => {
                keep = true;
            }
            other if other.starts_with('-') => {
                return Err(format!("unknown option: {}", other).into());
            }
            // positional size for convenience: ramdisk create 512
            other => {
                if size_mb == 512 {
                    if let Ok(n) = other
                        .trim_end_matches(|c: char| matches!(c, 'm' | 'M' | 'b' | 'B'))
                        .parse::<u64>()
                    {
                        size_mb = n;
                    } else {
                        return Err(format!("unexpected argument: {}", other).into());
                    }
                } else {
                    return Err(format!("unexpected argument: {}", other).into());
                }
            }
        }
        i += 1;
    }

    if size_mb == 0 {
        return Err("size must be greater than 0".into());
    }

    let opts = RamDiskOptions {
        size_mb,
        mount_point: mount,
        ..Default::default()
    };

    println!("Creating {} MiB ramdisk…", size_mb);
    let rd = RamDisk::new(opts)?;

    let info = rd.get_data();
    if !info.success {
        return Err("ramdisk creation reported failure".into());
    }

    println!("  mount point : {}", info.mount_point.display());
    if let Some(ref dev) = info.device {
        println!("  device      : {}", dev);
    }
    println!("  version     : {}", rd.version());

    if keep {
        println!();
        println!("Ramdisk is mounted. Press Enter to unmount and exit…");
        let _ = io::stdout().flush();
        let mut line = String::new();
        let _ = io::stdin().read_line(&mut line);
        println!("Unmounting…");
        rd.umount()?;
        println!("Done.");
    } else {
        // Leave the ramdisk mounted after this process exits.
        let info = rd.detach();
        println!();
        println!("Ramdisk left mounted (process can exit safely).");
        println!(
            "To unmount later:  ramdisk umount {}",
            info.mount_point.display()
        );
    }

    Ok(())
}

fn cmd_list() -> Result<(), Box<dyn std::error::Error>> {
    let list = list_mounted()?;
    if list.is_empty() {
        println!("No ramdisks found.");
        return Ok(());
    }
    println!("{:<40} {}", "MOUNT POINT", "DEVICE");
    println!("{:-<40} {}", "", "------");
    for m in &list {
        let dev = m.device.as_deref().unwrap_or("-");
        println!("{:<40} {}", m.mount_point.display(), dev);
    }
    Ok(())
}

fn cmd_umount(args: &[String]) -> Result<(), Box<dyn std::error::Error>> {
    if args.is_empty() {
        return Err("umount requires a mount point or device path".into());
    }
    let path = PathBuf::from(&args[0]);
    println!("Unmounting {}…", path.display());
    umount_path(&path)?;
    println!("Done.");
    Ok(())
}

fn cmd_info() -> Result<(), Box<dyn std::error::Error>> {
    println!("ramdisk {}", env!("CARGO_PKG_VERSION"));
    println!(
        "platform : {}",
        if cfg!(target_os = "linux") {
            "linux (tmpfs)"
        } else if cfg!(target_os = "macos") {
            "macos (hdiutil/APFS)"
        } else if cfg!(target_os = "windows") {
            "windows (AIM / aim_ll)"
        } else {
            "unsupported"
        }
    );
    println!("crate    : {}", env!("CARGO_PKG_NAME"));
    Ok(())
}
