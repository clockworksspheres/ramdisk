use std::path::PathBuf;

/// Options for creating a ramdisk.
#[derive(Debug, Clone)]
pub struct RamDiskOptions {
    /// Size of the ramdisk in mebibytes (MiB). Must be > 0.
    pub size_mb: u64,

    /// Optional explicit mount point. If `None` a temporary directory
    /// under the system temp dir is created and used.
    pub mount_point: Option<PathBuf>,

    /// Linux-only: filesystem type (`tmpfs` or `ramfs`). Defaults to `tmpfs`.
    pub linux_fstype: LinuxFsType,

    /// Linux-only: directory mode (octal). Defaults to 0o700.
    pub linux_mode: u32,

    /// Linux-only: uid that should own the mount (None = current user).
    pub linux_uid: Option<u32>,

    /// Linux-only: gid that should own the mount (None = current group).
    pub linux_gid: Option<u32>,

    /// macOS-only: disable APFS journaling after creation (experimental).
    pub macos_disable_journal: bool,

    /// Windows-only: filesystem type passed to AIM (default "ntfs").
    pub windows_fstype: String,
}

impl Default for RamDiskOptions {
    fn default() -> Self {
        Self {
            size_mb: 512,
            mount_point: None,
            linux_fstype: LinuxFsType::Tmpfs,
            linux_mode: 0o700,
            linux_uid: None,
            linux_gid: None,
            macos_disable_journal: false,
            windows_fstype: "ntfs".to_string(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LinuxFsType {
    Tmpfs,
    Ramfs,
}

impl LinuxFsType {
    pub fn as_str(self) -> &'static str {
        match self {
            LinuxFsType::Tmpfs => "tmpfs",
            LinuxFsType::Ramfs => "ramfs",
        }
    }
}

/// Information about a mounted ramdisk.
#[derive(Debug, Clone)]
pub struct MountInfo {
    pub success: bool,
    pub mount_point: PathBuf,
    pub device: Option<String>,
}

/// Best-effort free-memory check using /proc/meminfo (Linux) or a conservative default.
pub(crate) fn check_memory(size_mb: u64) -> crate::Result<()> {
    #[cfg(target_os = "linux")]
    {
        if let Ok(content) = std::fs::read_to_string("/proc/meminfo") {
            for line in content.lines() {
                if line.starts_with("MemAvailable:") {
                    let kb: u64 = line
                        .split_whitespace()
                        .nth(1)
                        .and_then(|s| s.parse().ok())
                        .unwrap_or(0);
                    let free_mb = kb / 1024;
                    if free_mb < size_mb {
                        return Err(crate::Error::MemoryNotAvailable {
                            requested: size_mb,
                            available: free_mb,
                        });
                    }
                    return Ok(());
                }
            }
        }
    }
    // On other platforms we skip the hard check; the OS tools will fail if
    // memory is truly exhausted.
    let _ = size_mb;
    Ok(())
}

/// Create a temporary directory that will be used as mount point.
pub(crate) fn random_mount_point() -> crate::Result<PathBuf> {
    let mut path = std::env::temp_dir();
    let unique = format!(
        "ramdisk-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0)
    );
    path.push(unique);
    std::fs::create_dir_all(&path)?;
    Ok(path)
}

/// Locate an executable on PATH (minimal re-implementation of `which`).
pub(crate) fn find_bin(name: &str) -> crate::Result<PathBuf> {
    if let Ok(path_var) = std::env::var("PATH") {
        for dir in std::env::split_paths(&path_var) {
            let candidate = dir.join(name);
            if candidate.is_file() {
                return Ok(candidate);
            }
            // Windows also looks for .exe
            #[cfg(target_os = "windows")]
            {
                let candidate_exe = dir.join(format!("{}.exe", name));
                if candidate_exe.is_file() {
                    return Ok(candidate_exe);
                }
            }
        }
    }
    // Absolute fallbacks common on Unix
    for prefix in &["/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin"] {
        let candidate = PathBuf::from(prefix).join(name);
        if candidate.is_file() {
            return Ok(candidate);
        }
    }
    Err(crate::Error::ToolNotFound(name.to_string()))
}
