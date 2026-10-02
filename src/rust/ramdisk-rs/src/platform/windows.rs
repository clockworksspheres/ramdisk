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
        let _ = Command::new(&aim).args(["-R", "-u", target]).output();
        self.mounted = false;
        let _ = std::fs::remove_dir(&self.mount_point);
        Ok(())
    }
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
    let stdout = String::from_utf8_lossy(&output.stdout);

    let mut result = Vec::new();
    for line in stdout.lines() {
        let lower = line.to_lowercase();
        if lower.contains("memory") || lower.contains("ram") {
            if let Some(dev) = line.split_whitespace().next() {
                result.push(MountInfo {
                    success: true,
                    mount_point: PathBuf::new(),
                    device: Some(dev.to_string()),
                });
            }
        }
    }
    Ok(result)
}

pub fn umount_path(path: &Path) -> Result<()> {
    let aim = find_bin("aim_ll").or_else(|_| find_bin("aim_ll.exe"))?;
    let output = Command::new(&aim)
        .args(["-R", "-u", path.to_str().unwrap_or("")])
        .output()?;
    if !output.status.success() {
        return Err(Error::CommandFailed {
            cmd: format!("aim_ll -R -u {}", path.display()),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
            status: format!("{:?}", output.status),
        });
    }
    Ok(())
}
