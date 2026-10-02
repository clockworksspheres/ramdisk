//! Windows ramdisk via Arsenal Image Mounter (aim_ll).
//! aim_ll.exe must be on PATH.
//! https://github.com/ArsenalRecon/Arsenal-Image-Mounter

use std::path::{Path, PathBuf};
use std::process::Command;

use crate::common::{check_memory, find_bin, random_mount_point, MountInfo, RamDiskOptions};
use crate::error::{Error, Result};
use super::PlatformRamDisk;

const VERSION: &str = "0.2.0-windows-aim";

pub struct WinAimRamDisk {
    success: bool,
    mount_point: PathBuf,
    device: Option<String>,
    mounted: bool,
}

impl WinAimRamDisk {
    pub fn new(opts: RamDiskOptions) -> Result<Self> {
        check_memory(opts.size_mb)?;

        let aim = find_bin("aim_ll")
            .or_else(|_| find_bin("aim_ll.exe"))
            .map_err(|_| Error::ToolNotFound(
                "aim_ll (Arsenal Image Mounter) – https://github.com/ArsenalRecon/Arsenal-Image-Mounter".into()
            ))?;

        let mount_point = match opts.mount_point {
            Some(p) => {
                if !p.exists() {
                    std::fs::create_dir_all(&p)?;
                }
                p
            }
            None => random_mount_point()?,
        };

        let mut this = Self {
            success: false,
            mount_point: mount_point.clone(),
            device: None,
            mounted: false,
        };

        this.create(&aim, opts.size_mb, &opts.windows_fstype)?;
        this.success = true;
        this.mounted = true;
        Ok(this)
    }

    fn create(&mut self, aim: &Path, size_mb: u64, fstype: &str) -> Result<()> {
        let size_arg = format!("{}M", size_mb);
        let mount_str = self.mount_point.to_string_lossy().replace('/', "\\");
        let params = format!("/fs:{} /q /y", fstype);

        let output = Command::new(aim)
            .args(["-a", "-s", &size_arg, "-m", &mount_str, "-p", &params])
            .output()?;

        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        let stderr = String::from_utf8_lossy(&output.stderr).to_string();

        if !output.status.success() {
            return Err(Error::CommandFailed {
                cmd: format!("aim_ll -a -s {}M -m {} ...", size_mb, mount_str),
                stdout,
                stderr,
                status: format!("{:?}", output.status),
            });
        }

        // Parse "Created device X"
        for line in stdout.lines() {
            let lower = line.to_lowercase();
            if lower.contains("created device") {
                let parts: Vec<&str> = line.split_whitespace().collect();
                if parts.len() >= 3 {
                    self.device = Some(parts[2].to_string());
                    break;
                }
            }
        }
        Ok(())
    }

    fn do_umount(&mut self) -> Result<()> {
        if !self.mounted {
            return Ok(());
        }
        let aim = find_bin("aim_ll").or_else(|_| find_bin("aim_ll.exe"))?;
        let target = self
            .device
            .as_deref()
            .unwrap_or_else(|| self.mount_point.to_str().unwrap_or(""));
        let (device, mount_point) = resolve_target(&aim, target)?;
        let output = Command::new(&aim).args(["-R", "-u", &device]).output()?;
        if !output.status.success() {
            return Err(command_failed(format!("aim_ll -R -u {}", device), &output));
        }

        self.mounted = false;
        self.success = false;
        detach_mount_point(mount_point.as_deref().unwrap_or(&self.mount_point))?;
        Ok(())
    }
}

fn command_failed(cmd: String, output: &std::process::Output) -> Error {
    Error::CommandFailed {
        cmd,
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        status: format!("{:?}", output.status),
    }
}

fn detach_mount_point(mount_point: &Path) -> Result<()> {
    let mount = mount_point.to_string_lossy();
    if mount.len() <= 3 {
        return Ok(());
    }

    let output = Command::new("mountvol")
        .arg(mount.as_ref())
        .arg("/D")
        .output()?;
    if !output.status.success() {
        return Err(command_failed(format!("mountvol {} /D", mount), &output));
    }
    Ok(())
}

fn query_mount_point(aim: &Path, device: &str) -> Result<Option<PathBuf>> {
    let output = Command::new(aim).args(["-l", "-u", device]).output()?;
    if !output.status.success() {
        return Ok(None);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    Ok(stdout.lines().find_map(|line| {
        line.trim()
            .strip_prefix("Mounted at ")
            .map(PathBuf::from)
    }))
}

fn normalized_mount_point(path: &Path) -> String {
    let absolute = if path.is_absolute() {
        path.to_path_buf()
    } else {
        std::env::current_dir()
            .map(|current_dir| current_dir.join(path))
            .unwrap_or_else(|_| path.to_path_buf())
    };
    let absolute: PathBuf = absolute
        .components()
        .filter(|component| !matches!(component, std::path::Component::CurDir))
        .collect();
    absolute
        .to_string_lossy()
        .replace('/', "\\")
        .trim_end_matches(['\\', '/'])
        .to_lowercase()
}

fn is_aim_device_id(value: &str) -> bool {
    value.len() == 6 && value.bytes().all(|byte| byte.is_ascii_digit())
}

fn resolve_target(aim: &Path, target: &str) -> Result<(String, Option<PathBuf>)> {
    let looks_like_path = target.contains('\\') || target.contains('/') || target.contains(':');
    if is_aim_device_id(target) || !looks_like_path {
        let mount_point = query_mount_point(aim, target)?;
        return Ok((target.to_string(), mount_point));
    }

    for mount in list_mounted()? {
        let Some(device) = mount.device else { continue };
        if normalized_mount_point(&mount.mount_point)
            == normalized_mount_point(Path::new(target))
        {
            return Ok((device, Some(mount.mount_point)));
        }
    }

    Err(Error::Other(format!(
        "no AIM ramdisk found at mount point {}",
        target
    )))
}

impl PlatformRamDisk for WinAimRamDisk {
    fn success(&self) -> bool { self.success }
    fn mount_point(&self) -> &Path { &self.mount_point }
    fn device(&self) -> Option<&str> { self.device.as_deref() }
    fn try_umount(&mut self) -> Result<()> { self.do_umount() }
    fn version(&self) -> &str { VERSION }
}

pub fn list_mounted() -> Result<Vec<MountInfo>> {
    let aim = find_bin("aim_ll").or_else(|_| find_bin("aim_ll.exe"))?;
    let output = Command::new(&aim).args(["-l"]).output()?;
    if !output.status.success() {
        return Err(command_failed("aim_ll -l".to_string(), &output));
    }
    Ok(parse_mounted_devices(&String::from_utf8_lossy(&output.stdout)))
}

fn parse_mounted_devices(output: &str) -> Vec<MountInfo> {
    let mut result = Vec::new();
    let mut device = None;
    let mut mount_point = None;
    let mut is_ramdisk = false;

    let finish_device = |result: &mut Vec<MountInfo>,
                         device: &mut Option<String>,
                         mount_point: &mut Option<PathBuf>,
                         is_ramdisk: &mut bool| {
        if *is_ramdisk {
            if let Some(device) = device.take() {
                result.push(MountInfo {
                    success: true,
                    mount_point: mount_point.take().unwrap_or_default(),
                    device: Some(device),
                });
            }
        }
        *device = None;
        *mount_point = None;
        *is_ramdisk = false;
    };

    for line in output.lines() {
        let line = line.trim();
        if let Some(id) = line.strip_prefix("Device number ") {
            finish_device(&mut result, &mut device, &mut mount_point, &mut is_ramdisk);
            device = id.split_whitespace().next().map(str::to_owned);
            continue;
        }

        let lower = line.to_lowercase();
        if lower.contains("virtual memory") || lower.contains("ram") {
            is_ramdisk = true;
        }
        if let Some(path) = line.strip_prefix("Mounted at ") {
            mount_point = Some(PathBuf::from(path.trim_end_matches(['\\', '/'])));
        }
    }

    finish_device(&mut result, &mut device, &mut mount_point, &mut is_ramdisk);
    result
}

pub fn umount_path(path: &Path) -> Result<()> {
    let aim = find_bin("aim_ll").or_else(|_| find_bin("aim_ll.exe"))?;
    let target = path.to_string_lossy();
    let (device, mount_point) = resolve_target(&aim, &target)?;

    let output = Command::new(&aim).args(["-R", "-u", &device]).output()?;
    if !output.status.success() {
        return Err(command_failed(format!("aim_ll -R -u {}", device), &output));
    }
    if let Some(mount_point) = mount_point {
        detach_mount_point(&mount_point)?;
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{is_aim_device_id, normalized_mount_point, parse_mounted_devices};
    use std::path::Path;

    #[test]
    fn recognizes_aim_device_ids() {
        assert!(is_aim_device_id("000123"));
        assert!(!is_aim_device_id("R:"));
        assert!(!is_aim_device_id("12345"));
    }

    #[test]
    fn normalizes_windows_mount_point_comparison() {
        assert_eq!(
            normalized_mount_point(Path::new("C:\\RamDisk\\")),
            normalized_mount_point(Path::new("c:\\ramdisk")),
        );
    }

    #[test]
    fn parses_aim_device_number_and_mount_point_blocks() {
        let output = r#"Device number 000000
Device is \\?\PhysicalDrive1
No image file.
Size: 536870912 bytes (512 MB), Virtual Memory, HDD, Modified.
Contains volume \\?\Volume{0325ef1a-0000-0000-0000-100000000000}\
Mounted at C:\Users\test\ram0\

1 device found."#;

        let devices = parse_mounted_devices(output);
        assert_eq!(devices.len(), 1);
        assert_eq!(devices[0].device.as_deref(), Some("000000"));
        assert_eq!(
            devices[0].mount_point,
            Path::new("C:\\Users\\test\\ram0")
        );
    }

    #[test]
    fn matches_relative_mount_path_to_aim_absolute_path() {
        let relative = Path::new("./ram0");
        let absolute = std::env::current_dir().unwrap().join("ram0");
        assert_eq!(
            normalized_mount_point(relative),
            normalized_mount_point(&absolute)
        );
    }
}
