//! macOS ramdisk implementation using hdiutil + diskutil.
//!
//! Sequence:
//!   1. hdiutil attach -nomount ram://<sectors>
//!   2. diskutil erasevolume APFS <unique-name> <device>
//!      → mounts at /Volumes/<unique-name>
//!   3. Discover the volume device (e.g. /dev/disk4s1) from `mount` output
//!   4. If custom mount point:
//!        diskutil unmount force /Volumes/<name>
//!        sleep
//!        diskutil mount -mountPoint <path> <volume-device>

use std::path::{Path, PathBuf};
use std::process::Command;
use std::thread;
use std::time::Duration;

use crate::common::{check_memory, find_bin, random_mount_point, MountInfo, RamDiskOptions};
use crate::error::{Error, Result};
use super::PlatformRamDisk;

const VERSION: &str = "0.2.0-macos-hdiutil";

pub struct MacRamDisk {
    success: bool,
    mount_point: PathBuf,
    /// Base device from hdiutil, e.g. /dev/disk4
    device: Option<String>,
    mounted: bool,
}

impl MacRamDisk {
    pub fn new(opts: RamDiskOptions) -> Result<Self> {
        check_memory(opts.size_mb)?;

        let custom_mount = opts.mount_point.is_some();
        let mount_point = match opts.mount_point {
            Some(ref p) => {
                if !p.exists() {
                    std::fs::create_dir_all(p)?;
                }
                p.clone()
            }
            None => random_mount_point()?,
        };

        let sectors = opts.size_mb.saturating_mul(1024 * 1024 / 512);
        if sectors == 0 {
            return Err(Error::SizeInvalid(opts.size_mb));
        }

        let mut this = Self {
            success: false,
            mount_point: mount_point.clone(),
            device: None,
            mounted: false,
        };

        this.create(sectors, custom_mount)?;
        this.success = true;
        this.mounted = true;
        Ok(this)
    }

    fn create(&mut self, sectors: u64, custom_mount: bool) -> Result<()> {
        let hdiutil = find_bin("hdiutil")?;
        let diskutil = find_bin("diskutil")?;

        // 1. Attach RAM device
        let attach_out = Command::new(&hdiutil)
            .args(["attach", "-nomount", &format!("ram://{}", sectors)])
            .output()?;

        if !attach_out.status.success() {
            return Err(cmd_err(
                format!("hdiutil attach -nomount ram://{}", sectors),
                &attach_out,
            ));
        }

        let base_dev = String::from_utf8_lossy(&attach_out.stdout)
            .trim()
            .lines()
            .next()
            .unwrap_or("")
            .trim()
            .to_string();

        if base_dev.is_empty() || !base_dev.starts_with("/dev/") {
            return Err(Error::Other(format!(
                "hdiutil returned unexpected device: {:?}",
                String::from_utf8_lossy(&attach_out.stdout)
            )));
        }
        self.device = Some(base_dev.clone());

        // Unique volume name to avoid collisions with prior runs
        let vol_name = format!(
            "RAMDisk-{}",
            std::process::id()
        );
        let volumes_path = PathBuf::from(format!("/Volumes/{}", vol_name));

        // 2. Format + auto-mount under /Volumes/<vol_name>
        let erase_out = Command::new(&diskutil)
            .args(["erasevolume", "APFS", &vol_name, &base_dev])
            .output()?;

        if !erase_out.status.success() {
            // Try HFS+ as fallback (works on older macOS)
            let erase_hfs = Command::new(&diskutil)
                .args(["erasevolume", "HFS+", &vol_name, &base_dev])
                .output()?;
            if !erase_hfs.status.success() {
                let _ = Command::new(&hdiutil)
                    .args(["detach", "-force", &base_dev])
                    .output();
                return Err(cmd_err(
                    format!("diskutil erasevolume APFS/HFS+ {} {}", vol_name, base_dev),
                    &erase_hfs,
                ));
            }
        }

        // Wait for /Volumes mount to appear
        for _ in 0..20 {
            if volumes_path.exists() {
                break;
            }
            thread::sleep(Duration::from_millis(100));
        }
        thread::sleep(Duration::from_millis(200));

        // 3. Discover the actual volume device node (e.g. /dev/disk4s1)
        let vol_dev = discover_volume_device(&volumes_path, &base_dev)
            .unwrap_or_else(|| format!("{}s1", base_dev));

        if !custom_mount {
            // Use the /Volumes path diskutil chose
            if volumes_path.exists() {
                self.mount_point = volumes_path;
            }
            return Ok(());
        }

        // 4. Custom mount point: unmount from /Volumes, remount at user path
        //    Unmount by mount-point path (most reliable), not unmountDisk.
        let mut unmounted = false;
        for attempt in 0..8 {
            let out = Command::new(&diskutil)
                .args([
                    "unmount",
                    "force",
                    volumes_path.to_str().unwrap_or(""),
                ])
                .output()?;
            if out.status.success() {
                unmounted = true;
                break;
            }
            // Also try by volume device
            let out2 = Command::new(&diskutil)
                .args(["unmount", "force", &vol_dev])
                .output()?;
            if out2.status.success() {
                unmounted = true;
                break;
            }
            thread::sleep(Duration::from_millis(150 * (attempt + 1) as u64));
        }

        if !unmounted && volumes_path.exists() {
            // One more try with unmountDisk
            let _ = Command::new(&diskutil)
                .args(["unmountDisk", "force", &base_dev])
                .output();
            thread::sleep(Duration::from_millis(400));
        }

        // Pause so the kernel finishes the unmount
        thread::sleep(Duration::from_millis(600));

        if !self.mount_point.exists() {
            std::fs::create_dir_all(&self.mount_point)?;
        }

        // Remount at user path – try volume device first, then base, then s1
        let candidates = [
            vol_dev.clone(),
            base_dev.clone(),
            format!("{}s1", base_dev),
        ];

        let mut mounted_ok = false;
        let mut last_out = None;

        for (i, target) in candidates.iter().enumerate() {
            if i > 0 {
                thread::sleep(Duration::from_millis(300));
            }
            let mount_out = Command::new(&diskutil)
                .args([
                    "mount",
                    "-mountPoint",
                    self.mount_point.to_str().unwrap_or(""),
                    target,
                ])
                .output()?;

            if mount_out.status.success() {
                mounted_ok = true;
                break;
            }
            last_out = Some(mount_out);
        }

        if !mounted_ok {
            // Last resort: mount_apfs / mount_hfs directly
            for (bin, target) in [
                ("mount_apfs", vol_dev.as_str()),
                ("mount_apfs", candidates[2].as_str()),
                ("mount_hfs", vol_dev.as_str()),
            ] {
                if let Ok(prog) = find_bin(bin) {
                    thread::sleep(Duration::from_millis(200));
                    let out = Command::new(&prog)
                        .args([target, self.mount_point.to_str().unwrap_or("")])
                        .output()?;
                    if out.status.success() {
                        mounted_ok = true;
                        break;
                    }
                    last_out = Some(out);
                }
            }
        }

        if !mounted_ok {
            let _ = Command::new(&hdiutil)
                .args(["detach", "-force", &base_dev])
                .output();
            if let Some(out) = last_out {
                return Err(cmd_err(
                    format!(
                        "diskutil mount -mountPoint {} {}",
                        self.mount_point.display(),
                        vol_dev
                    ),
                    &out,
                ));
            }
            return Err(Error::Other("mount failed".into()));
        }

        Ok(())
    }

    fn do_umount(&mut self) -> Result<()> {
        if !self.mounted {
            return Ok(());
        }

        let hdiutil = find_bin("hdiutil")?;
        if let Some(ref dev) = self.device {
            let output = Command::new(&hdiutil)
                .args(["detach", "-force", dev])
                .output()?;
            if !output.status.success() {
                if let Ok(du) = find_bin("diskutil") {
                    let _ = Command::new(&du)
                        .args(["unmountDisk", "force", dev])
                        .output();
                    thread::sleep(Duration::from_millis(300));
                    let _ = Command::new(&hdiutil)
                        .args(["detach", "-force", dev])
                        .output();
                }
            }
        }

        self.mounted = false;
        let _ = std::fs::remove_dir(&self.mount_point);
        Ok(())
    }
}

impl PlatformRamDisk for MacRamDisk {
    fn success(&self) -> bool {
        self.success
    }
    fn mount_point(&self) -> &Path {
        &self.mount_point
    }
    fn device(&self) -> Option<&str> {
        self.device.as_deref()
    }
    fn try_umount(&mut self) -> Result<()> {
        self.do_umount()
    }
    fn version(&self) -> &str {
        VERSION
    }
}

/// Find the /dev/diskXsY node currently mounted at `volumes_path`.
fn discover_volume_device(volumes_path: &Path, base_dev: &str) -> Option<String> {
    let mount_out = Command::new("mount").output().ok()?;
    let txt = String::from_utf8_lossy(&mount_out.stdout);
    let target = volumes_path.to_string_lossy();

    for line in txt.lines() {
        // Format: /dev/disk4s1 on /Volumes/RAMDisk-123 (apfs, local, ...)
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 3 && parts[1] == "on" && parts[2] == target.as_ref() {
            return Some(parts[0].to_string());
        }
    }

    // Fallback: diskutil info -plist is heavy; try diskutil list <base>
    let list_out = Command::new("diskutil")
        .args(["list", base_dev])
        .output()
        .ok()?;
    let list_txt = String::from_utf8_lossy(&list_out.stdout);
    // Look for a line with a slice device
    for line in list_txt.lines() {
        if let Some(dev) = line.split_whitespace().last() {
            if dev.starts_with("/dev/") && dev != base_dev {
                return Some(dev.to_string());
            }
            // diskutil list sometimes shows just "disk4s1"
            if dev.starts_with("disk") && dev.contains('s') {
                return Some(format!("/dev/{}", dev));
            }
        }
    }

    None
}

fn cmd_err(cmd: String, output: &std::process::Output) -> Error {
    Error::CommandFailed {
        cmd,
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        status: format!("{:?}", output.status),
    }
}

pub fn list_mounted() -> Result<Vec<MountInfo>> {
    // 1. Collect RAM-backed disk identifiers from hdiutil info / diskutil list
    let mut ram_bases: Vec<String> = Vec::new();

    // hdiutil info - shows images; ram:// entries include the disk id
    if let Ok(out) = Command::new("hdiutil").args(["info"]).output() {
        let txt = String::from_utf8_lossy(&out.stdout);
        let mut current_is_ram = false;
        for line in txt.lines() {
            let lower = line.to_lowercase();
            if lower.contains("ram://") || (lower.contains("image-path") && lower.contains("ram")) {
                current_is_ram = true;
            }
            if current_is_ram {
                // Look for "/dev/diskN" in this block
                for token in line.split_whitespace() {
                    if token.starts_with("/dev/disk") {
                        let base = strip_slice(token).to_string();
                        if !ram_bases.contains(&base) {
                            ram_bases.push(base);
                        }
                    }
                }
            }
            // hdiutil separates image blocks with ==== lines
            if line.starts_with("====") {
                current_is_ram = false;
            }
        }
    }

    // Also scan diskutil list for volumes named RAMDisk*
    if let Ok(out) = Command::new("diskutil").args(["list"]).output() {
        let txt = String::from_utf8_lossy(&out.stdout);
        let mut pending_name_is_ram = false;
        for line in txt.lines() {
            if line.contains("RAMDisk") || line.contains("RAMDISK") {
                pending_name_is_ram = true;
            }
            if pending_name_is_ram {
                if let Some(dev) = line.split_whitespace().last() {
                    if dev.starts_with("/dev/disk") || (dev.starts_with("disk") && dev.chars().any(|c| c.is_ascii_digit())) {
                        let full = if dev.starts_with("/dev/") {
                            dev.to_string()
                        } else {
                            format!("/dev/{}", dev)
                        };
                        let base = strip_slice(&full).to_string();
                        if !ram_bases.contains(&base) {
                            ram_bases.push(base);
                        }
                        pending_name_is_ram = false;
                    }
                }
            }
        }
    }

    // 2. Cross-reference with `mount` table: any mount whose device belongs to a RAM base
    let mount_out = Command::new("mount").output()?;
    let mount_txt = String::from_utf8_lossy(&mount_out.stdout);

    let mut result = Vec::new();
    for line in mount_txt.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 3 {
            continue;
        }
        let dev = parts[0];
        let mnt = parts[2];

        let is_ram = ram_bases.iter().any(|b| {
            dev == b || dev.starts_with(&(b.clone() + "s")) || strip_slice(dev) == b
        }) || mnt.starts_with("/Volumes/RAMDisk");

        if is_ram {
            let already = result.iter().any(|m: &MountInfo| m.mount_point == PathBuf::from(mnt));
            if !already {
                result.push(MountInfo {
                    success: true,
                    mount_point: PathBuf::from(mnt),
                    device: Some(dev.to_string()),
                });
            }
        }
    }

    Ok(result)
}

pub fn umount_path(path: &Path) -> Result<()> {
    let hdiutil = find_bin("hdiutil")?;
    let diskutil = find_bin("diskutil")?;
    let path_str = path.to_str().unwrap_or("");

    // Unmount by path or device
    let _ = Command::new(&diskutil)
        .args(["unmount", "force", path_str])
        .output();

    let base = if path_str.starts_with("/dev/") {
        strip_slice(path_str).to_string()
    } else {
        // Resolve device from mount table
        let mut found = None;
        if let Ok(mount_out) = Command::new("mount").output() {
            let txt = String::from_utf8_lossy(&mount_out.stdout);
            for line in txt.lines() {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 3 && parts[2] == path_str {
                    found = Some(strip_slice(parts[0]).to_string());
                    break;
                }
            }
        }
        found.unwrap_or_default()
    };

    if !base.is_empty() {
        thread::sleep(Duration::from_millis(200));
        // unmountDisk then detach
        let _ = Command::new(&diskutil)
            .args(["unmountDisk", "force", &base])
            .output();
        thread::sleep(Duration::from_millis(200));
        let _ = Command::new(&hdiutil)
            .args(["detach", "-force", &base])
            .output();
    }

    Ok(())
}

fn strip_slice(dev: &str) -> &str {
    if let Some(idx) = dev.rfind('s') {
        if dev[idx + 1..].chars().all(|c| c.is_ascii_digit()) {
            return &dev[..idx];
        }
    }
    dev
}
