use std::path::Path;

use crate::common::{MountInfo, RamDiskOptions};
use crate::error::Result;

pub(crate) trait PlatformRamDisk: Send {
    fn success(&self) -> bool;
    fn mount_point(&self) -> &Path;
    fn device(&self) -> Option<&str>;
    fn try_umount(&mut self) -> Result<()>;
    fn version(&self) -> &str;
}

pub(crate) fn create(opts: RamDiskOptions) -> Result<Box<dyn PlatformRamDisk>> {
    #[cfg(target_os = "linux")]
    {
        return Ok(Box::new(linux::LinuxTmpfsRamDisk::new(opts)?));
    }

    #[cfg(target_os = "macos")]
    {
        return Ok(Box::new(macos::MacRamDisk::new(opts)?));
    }

    #[cfg(target_os = "windows")]
    {
        return Ok(Box::new(windows::WinAimRamDisk::new(opts)?));
    }

    #[cfg(not(any(target_os = "linux", target_os = "macos", target_os = "windows")))]
    {
        let _ = opts;
        Err(crate::Error::UnsupportedPlatform)
    }
}

pub(crate) fn list_mounted() -> Result<Vec<MountInfo>> {
    #[cfg(target_os = "linux")]
    {
        return linux::list_mounted();
    }

    #[cfg(target_os = "macos")]
    {
        return macos::list_mounted();
    }

    #[cfg(target_os = "windows")]
    {
        return windows::list_mounted();
    }

    #[cfg(not(any(target_os = "linux", target_os = "macos", target_os = "windows")))]
    {
        Err(crate::Error::UnsupportedPlatform)
    }
}

pub(crate) fn umount_path(path: &Path) -> Result<()> {
    #[cfg(target_os = "linux")]
    {
        return linux::umount_path(path);
    }

    #[cfg(target_os = "macos")]
    {
        return macos::umount_path(path);
    }

    #[cfg(target_os = "windows")]
    {
        return windows::umount_path(path);
    }

    #[cfg(not(any(target_os = "linux", target_os = "macos", target_os = "windows")))]
    {
        let _ = path;
        Err(crate::Error::UnsupportedPlatform)
    }
}

#[cfg(target_os = "linux")]
pub(crate) mod linux;

#[cfg(target_os = "macos")]
pub(crate) mod macos;

#[cfg(target_os = "windows")]
pub(crate) mod windows;
