/**
 * Qt 6 GUI entry point — port of Python ramdisk-setup.py / ui/main.py
 */

#include "CreateRamdiskWindow.hpp"

#include <QApplication>
#include <QPalette>
#include <QColor>
#include <QStyle>
#include <QDateTime>

#ifdef __linux__
#  include <cstdlib>
#endif

static bool isNight(int startHour = 18, int endHour = 6) {
    const int h = QDateTime::currentDateTime().time().hour();
    if (startHour > endHour) {
        return h >= startHour || h < endHour;
    }
    return h >= startHour && h < endHour;
}

static void setDarkPalette(QApplication& app) {
    QPalette p;
    p.setColor(QPalette::Window, QColor(53, 53, 53));
    p.setColor(QPalette::WindowText, Qt::white);
    p.setColor(QPalette::Base, QColor(42, 42, 42));
    p.setColor(QPalette::AlternateBase, QColor(66, 66, 66));
    p.setColor(QPalette::Text, Qt::white);
    p.setColor(QPalette::Button, QColor(53, 53, 53));
    p.setColor(QPalette::ButtonText, Qt::white);
    p.setColor(QPalette::Highlight, QColor(42, 130, 218));
    p.setColor(QPalette::HighlightedText, Qt::white);
    p.setColor(QPalette::ToolTipBase, Qt::white);
    p.setColor(QPalette::ToolTipText, Qt::white);
    p.setColor(QPalette::Link, QColor(42, 130, 218));
    app.setPalette(p);
}

int main(int argc, char* argv[]) {
#ifdef __linux__
    // Prefer xcb if Wayland causes Qt issues (matches Python ramdisk-setup.py)
    if (std::getenv("WAYLAND_DISPLAY") != nullptr ||
        (std::getenv("XDG_SESSION_TYPE") != nullptr &&
         std::string(std::getenv("XDG_SESSION_TYPE")) == "wayland")) {
        if (std::getenv("QT_QPA_PLATFORM") == nullptr) {
            qputenv("QT_QPA_PLATFORM", "xcb");
        }
    }
#endif

    QApplication app(argc, argv);
    app.setApplicationName("ramdisk");
    app.setOrganizationName("clockworksspheres");
    app.setApplicationVersion("2.0.0");

#ifdef Q_OS_WIN
    app.setStyle("Fusion");
#endif

    if (isNight()) {
        setDarkPalette(app);
    }

    CreateRamdiskWindow window;
    window.show();
    window.raise();
    window.activateWindow();

    return app.exec();
}
