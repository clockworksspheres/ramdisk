fn main() {
    #[cfg(feature = "gui")]
    {
        // API for cxx-qt-build 0.7.x
        use cxx_qt_build::{CxxQtBuilder, QmlModule};

        CxxQtBuilder::new()
            .qml_module(QmlModule {
                uri: "com.clockworksspheres.ramdisk",
                version_major: 1,
                version_minor: 0,
                rust_files: &["src/gui/controller.rs"],
                qml_files: &["qml/main.qml"],
                qrc_files: &[] as &[&str],
            })
            // Qt Network is often required by Qt Qml on macOS
            .qt_module("Network")
            .build();
    }
}
