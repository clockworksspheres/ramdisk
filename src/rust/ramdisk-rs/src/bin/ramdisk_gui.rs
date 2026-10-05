//! Graphical front-end for the ramdisk library (CXX-Qt + QML).
//!
//! Port of the Python PySide6 `ramdisk-setup.py` / `_CreateRamdisk` UI.
//!
//! ```bash
//! cargo run --features gui --bin ramdisk-gui
//! ```
//!
//! Requires Qt 6 (`qmake` on PATH, or set `QMAKE=/path/to/qmake`).

#[cfg(feature = "gui")]
fn main() {
    use cxx_qt::casting::Upcast;
    use cxx_qt_lib::{QGuiApplication, QQmlApplicationEngine, QQmlEngine, QUrl};
    use std::pin::Pin;

    // Reference the bridge module so the QObject type is linked into the binary
    let _ = std::any::type_name::<ramdisk::gui::controller::qobject::RamdiskController>();

    #[cfg(target_os = "linux")]
    {
        if std::env::var_os("WAYLAND_DISPLAY").is_some()
            || std::env::var("XDG_SESSION_TYPE").as_deref() == Ok("wayland")
        {
            std::env::set_var("QT_QPA_PLATFORM", "xcb");
        }
    }

    let mut app = QGuiApplication::new();
    let mut engine = QQmlApplicationEngine::new();

    if let Some(engine) = engine.as_mut() {
        engine.load(&QUrl::from(
            "qrc:/qt/qml/com/clockworksspheres/ramdisk/qml/main.qml",
        ));
    }

    if let Some(engine) = engine.as_mut() {
        let engine: Pin<&mut QQmlEngine> = engine.upcast_pin();
        engine
            .on_quit(|_| {
                println!("QML Quit");
            })
            .release();
    }

    if let Some(app) = app.as_mut() {
        app.exec();
    }
}

#[cfg(not(feature = "gui"))]
fn main() {
    eprintln!("ramdisk-gui requires the `gui` feature.");
    eprintln!("  cargo run --features gui --bin ramdisk-gui");
    std::process::exit(1);
}
