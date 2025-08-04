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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QStatusBar,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(497, 447)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"QWidget {\n"
"	background-color: #ADADAD;\n"
"}")
        self.actionConfigure = QAction(MainWindow)
        self.actionConfigure.setObjectName(u"actionConfigure")
        self.actionOpen_Specfile = QAction(MainWindow)
        self.actionOpen_Specfile.setObjectName(u"actionOpen_Specfile")
        self.actionSave_Specfile = QAction(MainWindow)
        self.actionSave_Specfile.setObjectName(u"actionSave_Specfile")
        self.actionStyle = QAction(MainWindow)
        self.actionStyle.setObjectName(u"actionStyle")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.createPushButton = QPushButton(self.centralwidget)
        self.createPushButton.setObjectName(u"createPushButton")
        self.createPushButton.setGeometry(QRect(340, 70, 121, 32))
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
        self.sizeLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border-style: outset;\n"
"	background-color: #e6e6e6;\n"
"    font: 12px black;\n"
"}")
        self.sizeHorizontalSlider = QSlider(self.centralwidget)
        self.sizeHorizontalSlider.setObjectName(u"sizeHorizontalSlider")
        self.sizeHorizontalSlider.setGeometry(QRect(10, 70, 160, 25))
        self.sizeHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sizeLabel = QLabel(self.centralwidget)
        self.sizeLabel.setObjectName(u"sizeLabel")
        self.sizeLabel.setGeometry(QRect(10, 35, 161, 21))
        self.mountLabel = QLabel(self.centralwidget)
        self.mountLabel.setObjectName(u"mountLabel")
        self.mountLabel.setGeometry(QRect(20, 110, 211, 16))
        self.mountLineEdit = QLineEdit(self.centralwidget)
        self.mountLineEdit.setObjectName(u"mountLineEdit")
        self.mountLineEdit.setGeometry(QRect(20, 140, 241, 21))
        self.mountLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border-style: outset;\n"
"	background-color: #e6e6e6;\n"
"    font: 12px black;\n"
"}")
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(20, 230, 451, 141))
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 497, 43))
        self.menubar.setAutoFillBackground(False)
        self.menubar.setNativeMenuBar(True)
        self.menuRamDisk = QMenu(self.menubar)
        self.menuRamDisk.setObjectName(u"menuRamDisk")
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuRamDisk.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuRamDisk.addAction(self.actionConfigure)
        self.menuFile.addAction(self.actionOpen_Specfile)
        self.menuFile.addAction(self.actionSave_Specfile)
        self.menuEdit.addAction(self.actionStyle)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.actionConfigure.setText(QCoreApplication.translate("MainWindow", u"Configure", None))
        self.actionOpen_Specfile.setText(QCoreApplication.translate("MainWindow", u"Open Specfile", None))
        self.actionSave_Specfile.setText(QCoreApplication.translate("MainWindow", u"Save Specfile", None))
        self.actionStyle.setText(QCoreApplication.translate("MainWindow", u"Style", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.createPushButton.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.rListPushButton.setText(QCoreApplication.translate("MainWindow", u"Ramdisk List", None))
        self.debugPushButton.setText(QCoreApplication.translate("MainWindow", u"Debug", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.sizeLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Size", None))
        self.mountLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Mount Point", None))
        self.menuRamDisk.setTitle(QCoreApplication.translate("MainWindow", u"RamDisk", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

