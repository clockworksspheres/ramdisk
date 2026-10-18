//! QObject bridge: size / mount point / create / eject / list / local auth.
//! Mirrors PySide6 `_CreateRamdisk` + `_LocalAuth`.

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
        #[qproperty(QString, device_list_text)]
        #[qproperty(QString, mount_list_text)]
        #[qproperty(i32, selected_row)]
        #[qproperty(i32, max_size_mb)]
        #[qproperty(i32, row_count)]
        /// True when the Local Auth dialog should be shown (Linux, non-root).
        #[qproperty(bool, auth_required)]
        /// Pre-filled username for the auth dialog.
        #[qproperty(QString, auth_username)]
        /// "create" or "eject" — which action resumes after auth.
        #[qproperty(QString, pending_action)]
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

        #[qinvokable]
        #[cxx_name = "deviceAt"]
        fn device_at(self: &RamdiskController, index: i32) -> QString;

        #[qinvokable]
        #[cxx_name = "mountAt"]
        fn mount_at(self: &RamdiskController, index: i32) -> QString;

        /// Called when Local Auth dialog is accepted with a password.
        #[qinvokable]
        #[cxx_name = "submitAuth"]
        fn submit_auth(self: Pin<&mut RamdiskController>, password: QString);

        /// Called when Local Auth dialog is cancelled.
        #[qinvokable]
        #[cxx_name = "cancelAuth"]
        fn cancel_auth(self: Pin<&mut RamdiskController>);

        /// Whether the process is already root (no dialog needed).
        #[qinvokable]
        #[cxx_name = "isRoot"]
        fn is_root_q(self: &RamdiskController) -> bool;
    }
}

use core::pin::Pin;
use cxx_qt::CxxQtType;
use cxx_qt_lib::QString;

use ramdisk::{list_mounted, umount_path, RamDisk, RamDiskOptions};

pub struct RamdiskControllerRust {
    size_mb: i32,
    mount_point: QString,
    status_message: QString,
    device_list_text: QString,
    mount_list_text: QString,
    selected_row: i32,
    max_size_mb: i32,
    row_count: i32,
    auth_required: bool,
    auth_username: QString,
    pending_action: QString,
    /// Held only while an elevated action is in progress; cleared after use.
    sudo_password: Option<String>,
}

impl Default for RamdiskControllerRust {
    fn default() -> Self {
        let max = available_mem_mb().unwrap_or(8192).min(i32::MAX as u64) as i32;
        let user = current_username();
        Self {
            size_mb: 512,
            mount_point: QString::from(""),
            status_message: QString::from("Ready"),
            device_list_text: QString::from(""),
            mount_list_text: QString::from(""),
            selected_row: -1,
            max_size_mb: max,
            row_count: 0,
            auth_required: false,
            auth_username: QString::from(user.as_str()),
            pending_action: QString::from(""),
            sudo_password: None,
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
    pub fn is_root_q(self: &Self) -> bool {
        is_root()
    }

    pub fn create_ramdisk(mut self: Pin<&mut Self>) {
        #[cfg(target_os = "linux")]
        {
            if !is_root() && self.rust().sudo_password.is_none() {
                self.as_mut()
                    .set_pending_action(QString::from("create"));
                self.as_mut().set_auth_required(true);
                self.as_mut()
                    .set_status_message(QString::from("Authentication required to create ramdisk"));
                return;
            }
        }
        self.as_mut().do_create();
    }

    pub fn eject_selected(mut self: Pin<&mut Self>) {
        #[cfg(target_os = "linux")]
        {
            if !is_root() && self.rust().sudo_password.is_none() {
                self.as_mut()
                    .set_pending_action(QString::from("eject"));
                self.as_mut().set_auth_required(true);
                self.as_mut()
                    .set_status_message(QString::from("Authentication required to eject ramdisk"));
                return;
            }
        }
        self.as_mut().do_eject();
    }

    pub fn submit_auth(mut self: Pin<&mut Self>, password: QString) {
        let pw = password.to_string();
        if pw.is_empty() {
            self.as_mut()
                .set_status_message(QString::from("Password cannot be empty"));
            return;
        }
        // Store for the pending action only
        self.as_mut().rust_mut().sudo_password = Some(pw);
        self.as_mut().set_auth_required(false);

        let action = self.as_ref().pending_action().to_string();
        if action == "eject" {
            self.as_mut().do_eject();
        } else {
            self.as_mut().do_create();
        }
        // Clear password from memory after the action
        self.as_mut().rust_mut().sudo_password = None;
        self.as_mut().set_pending_action(QString::from(""));
    }

    pub fn cancel_auth(mut self: Pin<&mut Self>) {
        self.as_mut().set_auth_required(false);
        self.as_mut().rust_mut().sudo_password = None;
        self.as_mut().set_pending_action(QString::from(""));
        self.as_mut()
            .set_status_message(QString::from("Authentication cancelled"));
    }

    fn do_create(mut self: Pin<&mut Self>) {
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
            sudo_password: self.rust().sudo_password.clone(),
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

    fn do_eject(mut self: Pin<&mut Self>) {
        let row = *self.as_ref().selected_row();
        let mounts = lines_of(self.as_ref().mount_list_text());
        let devices = lines_of(self.as_ref().device_list_text());
        let count = mounts.len().max(devices.len()) as i32;

        let row = if (row < 0 || row >= count) && count > 0 {
            self.as_mut().set_selected_row(0);
            0
        } else {
            row
        };

        if row < 0 || row >= count {
            self.as_mut()
                .set_status_message(QString::from("No ramdisks to eject"));
            return;
        }

        let idx = row as usize;
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

        #[cfg(target_os = "linux")]
        {
            ramdisk::set_pending_sudo_password(
                self.rust().sudo_password.clone(),
            );
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

fn is_root() -> bool {
    #[cfg(target_os = "linux")]
    {
        std::fs::read_to_string("/proc/self/status")
            .ok()
            .and_then(|s| {
                s.lines()
                    .find(|l| l.starts_with("Uid:"))
                    .and_then(|l| l.split_whitespace().nth(1)?.parse::<u32>().ok())
            })
            == Some(0)
    }
    #[cfg(not(target_os = "linux"))]
    {
        false
    }
}

fn current_username() -> String {
    std::env::var("USER")
        .or_else(|_| std::env::var("USERNAME"))
        .unwrap_or_else(|_| "user".into())
}
