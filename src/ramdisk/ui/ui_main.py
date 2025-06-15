# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QSlider,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(478, 308)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.createPushButton = QPushButton(self.centralwidget)
        self.createPushButton.setObjectName(u"createPushButton")
        self.createPushButton.setGeometry(QRect(339, 80, 121, 32))
        self.rListPushButton = QPushButton(self.centralwidget)
        self.rListPushButton.setObjectName(u"rListPushButton")
        self.rListPushButton.setGeometry(QRect(20, 190, 100, 32))
        self.debugPushButton = QPushButton(self.centralwidget)
        self.debugPushButton.setObjectName(u"debugPushButton")
        self.debugPushButton.setGeometry(QRect(190, 190, 100, 32))
        self.quitPushButton = QPushButton(self.centralwidget)
        self.quitPushButton.setObjectName(u"quitPushButton")
        self.quitPushButton.setGeometry(QRect(360, 190, 100, 32))
        self.titleLabel = QLabel(self.centralwidget)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setGeometry(QRect(200, 10, 101, 16))
        self.sizeLineEdit = QLineEdit(self.centralwidget)
        self.sizeLineEdit.setObjectName(u"sizeLineEdit")
        self.sizeLineEdit.setGeometry(QRect(180, 70, 81, 21))
        self.sizeHorizontalSlider = QSlider(self.centralwidget)
        self.sizeHorizontalSlider.setObjectName(u"sizeHorizontalSlider")
        self.sizeHorizontalSlider.setGeometry(QRect(10, 70, 160, 25))
        self.sizeHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sizeLabel = QLabel(self.centralwidget)
        self.sizeLabel.setObjectName(u"sizeLabel")
        self.sizeLabel.setGeometry(QRect(20, 50, 161, 16))
        self.mountLabel = QLabel(self.centralwidget)
        self.mountLabel.setObjectName(u"mountLabel")
        self.mountLabel.setGeometry(QRect(20, 110, 211, 16))
        self.mountLineEdit = QLineEdit(self.centralwidget)
        self.mountLineEdit.setObjectName(u"mountLineEdit")
        self.mountLineEdit.setGeometry(QRect(20, 140, 241, 21))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 478, 43))
        self.menubar.setAutoFillBackground(True)
        self.menubar.setNativeMenuBar(True)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.createPushButton.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.rListPushButton.setText(QCoreApplication.translate("MainWindow", u"Ramdisk List", None))
        self.debugPushButton.setText(QCoreApplication.translate("MainWindow", u"Debug", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.sizeLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Size", None))
        self.mountLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Mount Point", None))
    # retranslateUi

