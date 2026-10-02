//! Linux tmpfs / ramfs ramdisk implementation.

use std::path::{Path, PathBuf};
use std::process::Command;

use crate::common::{check_memory, find_bin, random_mount_point, LinuxFsType, MountInfo, RamDiskOptions};
use crate::error::{Error, Result};
use super::PlatformRamDisk;

const VERSION: &str = "0.2.0-linux-tmpfs";

pub struct LinuxTmpfsRamDisk {
    success: bool,
    mount_point: PathBuf,
    device: Option<String>,
    size_mb: u64,
    mounted: bool,
}

impl LinuxTmpfsRamDisk {
    pub fn new(opts: RamDiskOptions) -> Result<Self> {
        check_memory(opts.size_mb)?;

        let mount_point = match opts.mount_point {
            Some(p) => {
                if !p.exists() {
                    std::fs::create_dir_all(&p)?;
                }
                p
            }
            None => random_mount_point()?,
        };

        // uid/gid – fall back to 0 if we cannot determine (root will override)
        let uid = opts.linux_uid.unwrap_or_else(|| {
            std::fs::read_to_string("/proc/self/status")
                .ok()
                .and_then(|s| {
                    s.lines()
                        .find(|l| l.starts_with("Uid:"))
                        .and_then(|l| l.split_whitespace().nth(1)?.parse().ok())
                })
                .unwrap_or(0)
        });
        let gid = opts.linux_gid.unwrap_or_else(|| {
            std::fs::read_to_string("/proc/self/status")
                .ok()
                .and_then(|s| {
                    s.lines()
                        .find(|l| l.starts_with("Gid:"))
                        .and_then(|l| l.split_whitespace().nth(1)?.parse().ok())
                })
                .unwrap_or(0)
        });
        let mode = opts.linux_mode;
        let fstype = opts.linux_fstype;

        let mut this = Self {
            success: false,
            mount_point: mount_point.clone(),
            device: Some("/dev/tmpfs".to_string()),
            size_mb: opts.size_mb,
            mounted: false,
        };

        this.mount(fstype, mode, uid, gid)?;
        this.success = true;
        this.mounted = true;
        Ok(this)
    }

    fn mount(&mut self, fstype: LinuxFsType, mode: u32, uid: u32, gid: u32) -> Result<()> {
        let mount_bin = find_bin("mount")?;

        let mut cmd = Command::new(&mount_bin);
        cmd.arg("-t").arg(fstype.as_str());

        match fstype {
            LinuxFsType::Tmpfs => {
                let opts = format!(
                    "size={}m,uid={},gid={},mode={:o}",
                    self.size_mb, uid, gid, mode
                );
                cmd.arg("-o").arg(opts).arg("tmpfs").arg(&self.mount_point);
            }
            LinuxFsType::Ramfs => {
                cmd.arg("ramfs").arg(&self.mount_point);
            }
        }

        let output = cmd.output()?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();

            if stderr.to_lowercase().contains("permission denied") {
                // Check effective uid via /proc
                let euid = std::fs::read_to_string("/proc/self/status")
                    .ok()
                    .and_then(|s| {
                        s.lines()
                            .find(|l| l.starts_with("Uid:"))
                            .and_then(|l| l.split_whitespace().nth(1)?.parse::<u32>().ok())
                    })
                    .unwrap_or(1);
                if euid != 0 {
                    return Err(Error::PrivilegeRequired);
                }
            }

            return Err(Error::CommandFailed {
                cmd: format!("{:?}", cmd),
                stdout,
                stderr,
                status: format!("{:?}", output.status),
            });
        }
        Ok(())
    }

    fn do_umount(&mut self) -> Result<()> {
        if !self.mounted {
            return Ok(());
        }

        let umount_bin = find_bin("umount")?;
        let output = Command::new(&umount_bin)
            .arg(&self.mount_point)
            .output()?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            if !stderr.contains("not mounted") && !stderr.contains("not found") {
                return Err(Error::CommandFailed {
                    cmd: format!("umount {}", self.mount_point.display()),
                    stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                    stderr,
                    status: format!("{:?}", output.status),
                });
            }
        }

        self.mounted = false;
        let _ = std::fs::remove_dir(&self.mount_point);
        Ok(())
    }
}

impl PlatformRamDisk for LinuxTmpfsRamDisk {
    fn success(&self) -> bool { self.success }
    fn mount_point(&self) -> &Path { &self.mount_point }
    fn device(&self) -> Option<&str> { self.device.as_deref() }
    fn try_umount(&mut self) -> Result<()> { self.do_umount() }
    fn version(&self) -> &str { VERSION }
}

pub fn list_mounted() -> Result<Vec<MountInfo>> {
    let output = Command::new("mount").output()?;
    let stdout = String::from_utf8_lossy(&output.stdout);

    let mut result = Vec::new();
    let system_prefixes = ["/dev/shm", "/run", "/tmp", "/run/lock", "/var/snap"];

    for line in stdout.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 3 || parts[0] != "tmpfs" {
            continue;
        }
        let mnt = parts[2];
        if system_prefixes.iter().any(|p| mnt.starts_with(p)) || mnt.starts_with("/run/user/") {
            continue;
        }
        result.push(MountInfo {
            success: true,
            mount_point: PathBuf::from(mnt),
            device: Some("/dev/tmpfs".to_string()),
        });
    }
    Ok(result)
}

pub fn umount_path(path: &Path) -> Result<()> {
    let umount_bin = find_bin("umount")?;
    let output = Command::new(&umount_bin).arg(path).output()?;
    if !output.status.success() {
        return Err(Error::CommandFailed {
            cmd: format!("umount {}", path.display()),
            stdout: String::from_utf8_lossy(&output.stdout).to_string(),
            stderr: String::from_utf8_lossy(&output.stderr).to_string(),
            status: format!("{:?}", output.status),
        });
    }
    Ok(())
}
