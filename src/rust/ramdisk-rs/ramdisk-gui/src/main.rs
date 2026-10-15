//! Graphical front-end for the ramdisk library (CXX-Qt + QML).
//!
//! ```bash
//! cargo run -p ramdisk-gui
//! ```

mod controller;

use cxx_qt_lib::{QGuiApplication, QQmlApplicationEngine, QUrl};

fn main() {
    // Ensure the QObject bridge is linked into this binary
    let _ = std::any::type_name::<controller::qobject::RamdiskController>();

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

    // cxx-qt embeds QML under qrc:/qt/qml/<uri-with-slashes>/<qml_files path>
    let qml_url = QUrl::from("qrc:/qt/qml/com/clockworksspheres/ramdisk/qml/main.qml");

    if let Some(engine) = engine.as_mut() {
        engine.load(&qml_url);
    }

    if let Some(app) = app.as_mut() {
        app.exec();
    }
}
