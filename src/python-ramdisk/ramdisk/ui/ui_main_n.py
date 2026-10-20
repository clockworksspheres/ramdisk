# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_n.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSlider,
    QStatusBar, QTableWidget, QTableWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(497, 447)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet(u"")
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
        self.centralwidget.setAutoFillBackground(True)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.titleLabel = QLabel(self.centralwidget)
        self.titleLabel.setObjectName(u"titleLabel")

        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 2)

        self.sizeLabel = QLabel(self.centralwidget)
        self.sizeLabel.setObjectName(u"sizeLabel")

        self.gridLayout.addWidget(self.sizeLabel, 1, 0, 1, 1)

        self.sizeHorizontalSlider = QSlider(self.centralwidget)
        self.sizeHorizontalSlider.setObjectName(u"sizeHorizontalSlider")
        self.sizeHorizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.sizeHorizontalSlider, 2, 0, 1, 1)

        self.sizeLineEdit = QLineEdit(self.centralwidget)
        self.sizeLineEdit.setObjectName(u"sizeLineEdit")

        self.gridLayout.addWidget(self.sizeLineEdit, 2, 1, 1, 2)

        self.createPushButton = QPushButton(self.centralwidget)
        self.createPushButton.setObjectName(u"createPushButton")

        self.gridLayout.addWidget(self.createPushButton, 2, 3, 1, 1)

        self.mountLabel = QLabel(self.centralwidget)
        self.mountLabel.setObjectName(u"mountLabel")

        self.gridLayout.addWidget(self.mountLabel, 3, 0, 1, 3)

        self.mountLineEdit = QLineEdit(self.centralwidget)
        self.mountLineEdit.setObjectName(u"mountLineEdit")

        self.gridLayout.addWidget(self.mountLineEdit, 4, 0, 1, 2)

        self.ejectPushButton = QPushButton(self.centralwidget)
        self.ejectPushButton.setObjectName(u"ejectPushButton")

        self.gridLayout.addWidget(self.ejectPushButton, 5, 0, 1, 1)

        self.quitPushButton = QPushButton(self.centralwidget)
        self.quitPushButton.setObjectName(u"quitPushButton")

        self.gridLayout.addWidget(self.quitPushButton, 5, 3, 1, 1)

        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)

        self.gridLayout.addWidget(self.tableWidget, 6, 0, 1, 4)

        self.debugPushButton = QPushButton(self.centralwidget)
        self.debugPushButton.setObjectName(u"debugPushButton")
        self.debugPushButton.setEnabled(True)

        self.gridLayout.addWidget(self.debugPushButton, 5, 1, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 497, 30))
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
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.sizeLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Size", None))
        self.createPushButton.setText(QCoreApplication.translate("MainWindow", u"Create Ramdisk", None))
        self.mountLabel.setText(QCoreApplication.translate("MainWindow", u"Ramdisk Mount Point", None))
        self.mountLineEdit.setText(QCoreApplication.translate("MainWindow", u"put mountpoint here", None))
        self.ejectPushButton.setText(QCoreApplication.translate("MainWindow", u"Eject Ramdisk", None))
        self.quitPushButton.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.debugPushButton.setText(QCoreApplication.translate("MainWindow", u"Debug", None))
        self.menuRamDisk.setTitle(QCoreApplication.translate("MainWindow", u"RamDisk", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

