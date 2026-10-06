//! Cross-platform ramdisk library.
//!
//! Provides a uniform interface for creating and managing in-memory disks
//! (ramdisks) on Linux (tmpfs), macOS (hdiutil + APFS), and Windows
//! (Arsenal Image Mounter / AIM Toolkit).
//!
//! Ported from the Python project [clockworksspheres/ramdisk](https://github.com/clockworksspheres/ramdisk).
//!
//! # Example
//!
//! ```no_run
//! use ramdisk::{RamDisk, RamDiskOptions};
//!
//! let rd = RamDisk::new(RamDiskOptions {
//!     size_mb: 512,
//!     mount_point: None,
//!     ..Default::default()
//! })?;
//!
//! println!("Mounted at: {}", rd.mount_point().display());
//! println!("Device: {:?}", rd.device());
//!
//! // ... use the ramdisk ...
//!
//! rd.umount()?;
//! # Ok::<(), ramdisk::Error>(())
//! ```

mod error;
mod platform;
mod common;

#[cfg(feature = "gui")]
pub mod gui;

pub use error::{Error, Result};
pub use common::{RamDiskOptions, MountInfo, LinuxFsType};

use std::path::{Path, PathBuf};

/// Cross-platform ramdisk handle.
///
/// Instantiating a `RamDisk` creates and mounts an in-memory filesystem.
/// When the value is dropped (or `umount` is called) the ramdisk is
/// detached / unmounted.
pub struct RamDisk {
    inner: Box<dyn platform::PlatformRamDisk>,
}

impl RamDisk {
    /// Create and mount a new ramdisk with the given options.
    pub fn new(opts: RamDiskOptions) -> Result<Self> {
        if opts.size_mb == 0 {
            return Err(Error::SizeInvalid(opts.size_mb));
        }

        let inner = platform::create(opts)?;
        Ok(Self { inner })
    }

    /// Convenience constructor: size in MiB, random temporary mount point.
    pub fn with_size(size_mb: u64) -> Result<Self> {
        Self::new(RamDiskOptions {
            size_mb,
            ..Default::default()
        })
    }

    /// Convenience constructor: size in MiB and explicit mount point.
    pub fn with_size_and_mount(size_mb: u64, mount_point: impl Into<PathBuf>) -> Result<Self> {
        Self::new(RamDiskOptions {
            size_mb,
            mount_point: Some(mount_point.into()),
            ..Default::default()
        })
    }

    /// Returns whether the ramdisk was successfully created and mounted.
    pub fn success(&self) -> bool {
        self.inner.success()
    }

    /// Path where the ramdisk is mounted.
    pub fn mount_point(&self) -> &Path {
        self.inner.mount_point()
    }

    /// Underlying device identifier (e.g. `/dev/disk4` on macOS, empty/tmpfs on Linux).
    pub fn device(&self) -> Option<&str> {
        self.inner.device()
    }

    /// Tuple of (success, mount_point, device) – mirrors the original Python `getData()`.
    pub fn get_data(&self) -> MountInfo {
        MountInfo {
            success: self.success(),
            mount_point: self.mount_point().to_path_buf(),
            device: self.device().map(str::to_owned),
        }
    }

    /// Unmount / detach the ramdisk.
    ///
    /// Consumes the handle. Prefer this over relying on `Drop` when you need
    /// to handle errors from the unmount operation.
    ///
    /// After a successful call the OS resources are released and the
    /// subsequent `Drop` is a no-op (platform implementations are idempotent).
    pub fn umount(mut self) -> Result<()> {
        self.inner.try_umount()
        // `self` is dropped here; Drop calls try_umount again, which is a
        // no-op because the platform type has already marked itself unmounted.
    }

    /// Attempt to unmount without consuming the handle (best-effort).
    pub fn try_umount(&mut self) -> Result<()> {
        self.inner.try_umount()
    }

    /// Release the handle **without** unmounting the ramdisk.
    ///
    /// The OS mount remains active until you call [`umount_path`] or
    /// otherwise unmount it. Use this when you want the ramdisk to outlive
    /// the process (e.g. a CLI that creates a mount and exits).
    ///
    /// Returns the mount point and device so the caller can record them.
    pub fn detach(self) -> MountInfo {
        let info = self.get_data();
        // Prevent Drop from unmounting.
        std::mem::forget(self);
        info
    }

    /// Library / platform-module version string.
    pub fn version(&self) -> &str {
        self.inner.version()
    }
}

impl Drop for RamDisk {
    fn drop(&mut self) {
        let _ = self.inner.try_umount();
    }
}

/// List currently mounted ramdisks (platform-specific heuristics).
pub fn list_mounted() -> Result<Vec<MountInfo>> {
    platform::list_mounted()
}

/// Unmount a ramdisk by mount-point or device path.
pub fn umount_path(path: impl AsRef<Path>) -> Result<()> {
    platform::umount_path(path.as_ref())
}
