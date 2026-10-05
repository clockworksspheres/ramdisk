fn main() {
    #[cfg(feature = "gui")]
    {
        use cxx_qt_build::{CxxQtBuilder, QmlModule};

        CxxQtBuilder::new_qml_module(
            QmlModule::new("com.clockworksspheres.ramdisk").qml_file("qml/main.qml"),
        )
        // Qt Network is required by Qt Qml on macOS
        .qt_module("Network")
        .files(["src/gui/controller.rs"])
        .build();
    }
}
