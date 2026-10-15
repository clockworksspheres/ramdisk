//! Linux tmpfs / ramfs ramdisk implementation.

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::Mutex;

use crate::common::{
    check_memory, find_bin, random_mount_point, LinuxFsType, MountInfo, RamDiskOptions,
};
use crate::error::{Error, Result};
use super::PlatformRamDisk;

const VERSION: &str = "0.2.0-linux-tmpfs";

/// Optional password for the next umount_path call (GUI sets this before eject).
static PENDING_SUDO: Mutex<Option<String>> = Mutex::new(None);

pub fn set_pending_sudo_password(pw: Option<String>) {
    if let Ok(mut g) = PENDING_SUDO.lock() {
        *g = pw;
    }
}

fn take_pending_sudo() -> Option<String> {
    PENDING_SUDO.lock().ok().and_then(|mut g| g.take())
}

pub struct LinuxTmpfsRamDisk {
    success: bool,
    mount_point: PathBuf,
    device: Option<String>,
    size_mb: u64,
    mounted: bool,
    sudo_password: Option<String>,
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

        let uid = opts.linux_uid.unwrap_or_else(|| current_uid());
        let gid = opts.linux_gid.unwrap_or_else(|| current_gid());
        let mode = opts.linux_mode;
        let fstype = opts.linux_fstype;
        let sudo_password = opts.sudo_password.clone();

        let mut this = Self {
            success: false,
            mount_point: mount_point.clone(),
            device: Some("/dev/tmpfs".to_string()),
            size_mb: opts.size_mb,
            mounted: false,
            sudo_password,
        };

        this.mount(fstype, mode, uid, gid)?;
        this.success = true;
        this.mounted = true;
        Ok(this)
    }

    fn mount(&mut self, fstype: LinuxFsType, mode: u32, uid: u32, gid: u32) -> Result<()> {
        let mount_bin = find_bin("mount")?;
        let mount_bin_s = mount_bin.to_string_lossy().into_owned();

        let mut args: Vec<String> = vec!["-t".into(), fstype.as_str().into()];
        match fstype {
            LinuxFsType::Tmpfs => {
                let opts = format!(
                    "size={}m,uid={},gid={},mode={:o}",
                    self.size_mb, uid, gid, mode
                );
                args.extend(["-o".into(), opts, "tmpfs".into(), self.mount_point.display().to_string()]);
            }
            LinuxFsType::Ramfs => {
                args.extend(["ramfs".into(), self.mount_point.display().to_string()]);
            }
        }

        let output = run_maybe_sudo(&mount_bin_s, &args, self.sudo_password.as_deref())?;

        if !output.status.success() {
            return Err(Error::CommandFailed {
                cmd: format!("{} {}", mount_bin_s, args.join(" ")),
                stdout: String::from_utf8_lossy(&output.stdout).to_string(),
                stderr: String::from_utf8_lossy(&output.stderr).to_string(),
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
        let umount_bin_s = umount_bin.to_string_lossy().into_owned();
        let args = vec![self.mount_point.display().to_string()];
        let output = run_maybe_sudo(&umount_bin_s, &args, self.sudo_password.as_deref())?;

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

pub fn list_mounted() -> Result<Vec<MountInfo>> {
    let output = Command::new("mount").output()?;
    let stdout = String::from_utf8_lossy(&output.stdout);

    let mut result = Vec::new();
    // Only skip well-known *system* tmpfs mounts. User ramdisks often live
    // under /tmp (tempfile default) so we must NOT blanket-exclude /tmp.
    let system_exact = [
        "/dev/shm",
        "/sys/fs/cgroup",
        "/tmp",           // the root /tmp mount itself, not children
        "/dev",
        "/run",
        "/run/lock",
        "/run/user",      // prefix handled below
        "/var/tmp",
    ];

    for line in stdout.lines() {
        let parts: Vec<&str> = line.split_whitespace().collect();
        // Typical: "tmpfs on /path type tmpfs (rw,...)"  OR  "tmpfs /path tmpfs rw,..."
        let mnt = if parts.len() >= 3 && parts[1] == "on" {
            parts[2]
        } else if parts.len() >= 2 && parts[0] == "tmpfs" {
            parts[1]
        } else {
            continue;
        };

        // Must be tmpfs (check type field when present)
        let is_tmpfs = parts[0] == "tmpfs"
            || parts.iter().any(|p| *p == "tmpfs")
            || line.contains("type tmpfs");
        if !is_tmpfs {
            continue;
        }

        if system_exact.iter().any(|p| mnt == *p) {
            continue;
        }
        if mnt.starts_with("/run/")
            || mnt.starts_with("/sys/")
            || mnt.starts_with("/dev/")
            || mnt.starts_with("/proc/")
            || mnt.starts_with("/var/lib/")
            || mnt.starts_with("/var/snap/")
        {
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
    let umount_bin_s = umount_bin.to_string_lossy().into_owned();
    let args = vec![path.display().to_string()];
    let pw = take_pending_sudo();
    let output = run_maybe_sudo(&umount_bin_s, &args, pw.as_deref())?;
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

/// Run `bin` with `args`. If not root and `password` is Some, use `sudo -S`.
fn run_maybe_sudo(
    bin: &str,
    args: &[String],
    password: Option<&str>,
) -> Result<std::process::Output> {
    if is_root() || password.is_none() {
        let mut cmd = Command::new(bin);
        for a in args {
            cmd.arg(a);
        }
        return Ok(cmd.output()?);
    }

    let password = password.unwrap();
    // sudo -k clears cached credentials; then sudo -S reads password from stdin
    let _ = Command::new("sudo").args(["-k"]).output();

    let mut cmd = Command::new("sudo");
    cmd.arg("-S")
        .arg("--")
        .arg(bin)
        .args(args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut child = cmd.spawn()?;
    if let Some(mut stdin) = child.stdin.take() {
        // sudo -S expects password + newline
        writeln!(stdin, "{password}")?;
    }
    Ok(child.wait_with_output()?)
}

fn is_root() -> bool {
    current_uid() == 0
}

fn current_uid() -> u32 {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| {
            s.lines()
                .find(|l| l.starts_with("Uid:"))
                .and_then(|l| l.split_whitespace().nth(1)?.parse().ok())
        })
        .unwrap_or(0)
}

fn current_gid() -> u32 {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| {
            s.lines()
                .find(|l| l.starts_with("Gid:"))
                .and_then(|l| l.split_whitespace().nth(1)?.parse().ok())
        })
        .unwrap_or(0)
}
