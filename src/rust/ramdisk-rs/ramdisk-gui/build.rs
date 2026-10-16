use cxx_qt_build::{CxxQtBuilder, QmlModule};
use std::env;
use std::process::Command;

fn main() {
    if env::var_os("QMAKE").is_none() {
        for candidate in ["qmake6", "qmake"] {
            if let Ok(output) = Command::new(candidate).arg("-query").arg("QT_VERSION").output() {
                if output.status.success() {
                    if let Ok(path) = which(candidate) {
                        println!("cargo:warning=cxx-qt-build: using QMAKE={path}");
                        env::set_var("QMAKE", &path);
                        break;
                    }
                }
            }
        }
    }

    // Relative paths so qrc layout is:
    //   qrc:/qt/qml/com/clockworksspheres/ramdisk/qml/main.qml
    CxxQtBuilder::new()
        .qml_module(QmlModule {
            uri: "com.clockworksspheres.ramdisk",
            version_major: 1,
            version_minor: 0,
            rust_files: &["src/controller.rs"],
            qml_files: &["qml/main.qml"],
            qrc_files: &[] as &[&str],
        })
        .qt_module("Network")
        .build();

    // Linux: libstdc++; macOS/BSD: libc++ (usually already linked as -lc++)
    let target = env::var("TARGET").unwrap_or_default();
    if target.contains("linux") {
        println!("cargo:rustc-link-lib=stdc++");
    } else if target.contains("apple") || target.contains("darwin") {
        println!("cargo:rustc-link-lib=c++");
    }

    println!("cargo:rerun-if-changed=src/controller.rs");
    println!("cargo:rerun-if-changed=qml/main.qml");
}

fn which(cmd: &str) -> Result<String, ()> {
    let output = Command::new("sh")
        .arg("-c")
        .arg(format!("command -v {cmd}"))
        .output()
        .map_err(|_| ())?;
    if !output.status.success() {
        return Err(());
    }
    let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if path.is_empty() {
        Err(())
    } else {
        Ok(path)
    }
}
