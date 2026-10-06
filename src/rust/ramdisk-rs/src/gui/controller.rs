//! QObject bridge: size / mount point / create / eject / list.
//! Mirrors `ramdisk.ui.main._CreateRamdisk` from the Python PySide6 UI.

#[cxx_qt::bridge]
pub mod qobject {
    unsafe extern "C++" {
        include!("cxx-qt-lib/qstring.h");
        type QString = cxx_qt_lib::QString;
    }

    extern "RustQt" {
        #[qobject]
        #[qml_element]
        #[qproperty(i32, size_mb)]
        #[qproperty(QString, mount_point)]
        #[qproperty(QString, status_message)]
        /// Newline-separated device paths (parallel to mount_list_text).
        #[qproperty(QString, device_list_text)]
        /// Newline-separated mount paths (parallel to device_list_text).
        #[qproperty(QString, mount_list_text)]
        #[qproperty(i32, selected_row)]
        #[qproperty(i32, max_size_mb)]
        #[qproperty(i32, row_count)]
        #[namespace = "ramdisk_gui"]
        type RamdiskController = super::RamdiskControllerRust;

        #[qinvokable]
        #[cxx_name = "createRamdisk"]
        fn create_ramdisk(self: Pin<&mut RamdiskController>);

        #[qinvokable]
        #[cxx_name = "ejectSelected"]
        fn eject_selected(self: Pin<&mut RamdiskController>);

        #[qinvokable]
        #[cxx_name = "refreshList"]
        fn refresh_list(self: Pin<&mut RamdiskController>);

        #[qinvokable]
        #[cxx_name = "setSizeFromSlider"]
        fn set_size_from_slider(self: Pin<&mut RamdiskController>, value: i32);

        /// Return the device string for row `index`.
        #[qinvokable]
        #[cxx_name = "deviceAt"]
        fn device_at(self: &RamdiskController, index: i32) -> QString;

        /// Return the mount-point string for row `index`.
        #[qinvokable]
        #[cxx_name = "mountAt"]
        fn mount_at(self: &RamdiskController, index: i32) -> QString;
    }
}

use core::pin::Pin;
use cxx_qt_lib::QString;

use crate::{list_mounted, umount_path, RamDisk, RamDiskOptions};

pub struct RamdiskControllerRust {
    size_mb: i32,
    mount_point: QString,
    status_message: QString,
    device_list_text: QString,
    mount_list_text: QString,
    selected_row: i32,
    max_size_mb: i32,
    row_count: i32,
}

impl Default for RamdiskControllerRust {
    fn default() -> Self {
        let max = available_mem_mb().unwrap_or(8192).min(i32::MAX as u64) as i32;
        Self {
            size_mb: 512,
            mount_point: QString::from(""),
            status_message: QString::from("Ready"),
            device_list_text: QString::from(""),
            mount_list_text: QString::from(""),
            selected_row: -1,
            max_size_mb: max,
            row_count: 0,
        }
    }
}

fn lines_of(s: &QString) -> Vec<String> {
    let t = s.to_string();
    if t.is_empty() {
        Vec::new()
    } else {
        t.lines().map(|l| l.to_string()).collect()
    }
}

impl qobject::RamdiskController {
    pub fn create_ramdisk(mut self: Pin<&mut Self>) {
        let size = *self.as_ref().size_mb();
        if size <= 0 {
            self.as_mut()
                .set_status_message(QString::from("Size must be greater than 0"));
            return;
        }

        let mount_str = self.as_ref().mount_point().to_string();
        let mount_opt = if mount_str.trim().is_empty()
            || mount_str == "put mountpoint here"
        {
            None
        } else {
            Some(std::path::PathBuf::from(mount_str.trim()))
        };

        let opts = RamDiskOptions {
            size_mb: size as u64,
            mount_point: mount_opt,
            ..Default::default()
        };

        match RamDisk::new(opts) {
            Ok(rd) => {
                let info = rd.detach();
                let msg = format!(
                    "Created {} MiB at {}",
                    size,
                    info.mount_point.display()
                );
                self.as_mut()
                    .set_status_message(QString::from(msg.as_str()));
                self.as_mut().refresh_list();
            }
            Err(e) => {
                self.as_mut()
                    .set_status_message(QString::from(format!("Error: {e}").as_str()));
            }
        }
    }

    pub fn eject_selected(mut self: Pin<&mut Self>) {
        let row = *self.as_ref().selected_row();
        let mounts = lines_of(self.as_ref().mount_list_text());
        let devices = lines_of(self.as_ref().device_list_text());
        let count = mounts.len().max(devices.len()) as i32;

        // Default to the first mounted disk when nothing is selected
        let row = if (row < 0 || row >= count) && count > 0 {
            self.as_mut().set_selected_row(0);
            0
        } else {
            row
        };

        if row < 0 || row >= count {
            self.as_mut().set_status_message(QString::from(
                "No ramdisks to eject",
            ));
            return;
        }

        let idx = row as usize;
        // Prefer mount path; fall back to device node (macOS eject resolves both)
        let path = mounts
            .get(idx)
            .filter(|s| !s.is_empty())
            .cloned()
            .or_else(|| devices.get(idx).cloned())
            .unwrap_or_default();

        if path.trim().is_empty() {
            self.as_mut()
                .set_status_message(QString::from("Selected row has no mount path or device"));
            return;
        }

        match umount_path(std::path::Path::new(path.trim())) {
            Ok(()) => {
                self.as_mut()
                    .set_status_message(QString::from(format!("Ejected {path}").as_str()));
                self.as_mut().set_selected_row(-1);
                self.as_mut().refresh_list();
            }
            Err(e) => {
                self.as_mut()
                    .set_status_message(QString::from(format!("Eject error: {e}").as_str()));
            }
        }
    }

    pub fn refresh_list(mut self: Pin<&mut Self>) {
        // Reset first so QML sees a row_count change even if count is unchanged
        self.as_mut().set_row_count(0);

        match list_mounted() {
            Ok(list) => {
                let mut devs = Vec::new();
                let mut mnts = Vec::new();
                for m in &list {
                    devs.push(m.device.clone().unwrap_or_else(|| "-".into()));
                    mnts.push(m.mount_point.to_string_lossy().into_owned());
                }
                let count = list.len() as i32;
                self.as_mut()
                    .set_device_list_text(QString::from(devs.join("\n").as_str()));
                self.as_mut()
                    .set_mount_list_text(QString::from(mnts.join("\n").as_str()));
                self.as_mut().set_row_count(count);
                // Default selection: first mounted disk
                if count > 0 {
                    self.as_mut().set_selected_row(0);
                } else {
                    self.as_mut().set_selected_row(-1);
                }
                self.as_mut().set_status_message(QString::from(
                    format!("Found {count} ramdisk(s)").as_str(),
                ));
            }
            Err(e) => {
                self.as_mut().set_device_list_text(QString::from(""));
                self.as_mut().set_mount_list_text(QString::from(""));
                self.as_mut().set_row_count(0);
                self.as_mut()
                    .set_status_message(QString::from(format!("List error: {e}").as_str()));
            }
        }
    }
    pub fn set_size_from_slider(self: Pin<&mut Self>, value: i32) {
        self.set_size_mb(value.max(0));
    }

    pub fn device_at(self: &Self, index: i32) -> QString {
        lines_of(self.device_list_text())
            .get(index as usize)
            .map(|s| QString::from(s.as_str()))
            .unwrap_or_default()
    }

    pub fn mount_at(self: &Self, index: i32) -> QString {
        lines_of(self.mount_list_text())
            .get(index as usize)
            .map(|s| QString::from(s.as_str()))
            .unwrap_or_default()
    }
}

fn available_mem_mb() -> Option<u64> {
    #[cfg(target_os = "linux")]
    {
        let content = std::fs::read_to_string("/proc/meminfo").ok()?;
        for line in content.lines() {
            if line.starts_with("MemAvailable:") {
                let kb: u64 = line.split_whitespace().nth(1)?.parse().ok()?;
                return Some(kb / 1024);
            }
        }
        None
    }
    #[cfg(not(target_os = "linux"))]
    {
        Some(8192)
    }
}
