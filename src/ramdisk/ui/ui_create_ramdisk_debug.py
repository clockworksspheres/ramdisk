# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_ramdisk_debug.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QSlider, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(301, 234)
        self.sizeLineEdit = QLineEdit(Form)
        self.sizeLineEdit.setObjectName(u"sizeLineEdit")
        self.sizeLineEdit.setGeometry(QRect(180, 40, 51, 21))
        self.sizeHorizontalSlider = QSlider(Form)
        self.sizeHorizontalSlider.setObjectName(u"sizeHorizontalSlider")
        self.sizeHorizontalSlider.setGeometry(QRect(10, 40, 160, 25))
        self.sizeHorizontalSlider.setOrientation(Qt.Horizontal)
        self.createPushButton = QPushButton(Form)
        self.createPushButton.setObjectName(u"createPushButton")
        self.createPushButton.setGeometry(QRect(30, 150, 131, 32))
        self.mountLineEdit = QLineEdit(Form)
        self.mountLineEdit.setObjectName(u"mountLineEdit")
        self.mountLineEdit.setGeometry(QRect(10, 100, 221, 21))
        self.mountLabel = QLabel(Form)
        self.mountLabel.setObjectName(u"mountLabel")
        self.mountLabel.setGeometry(QRect(10, 80, 81, 16))
        self.randomRadioButton = QRadioButton(Form)
        self.randomRadioButton.setObjectName(u"randomRadioButton")
        self.randomRadioButton.setGeometry(QRect(100, 80, 99, 20))
        self.sizeLabel = QLabel(Form)
        self.sizeLabel.setObjectName(u"sizeLabel")
        self.sizeLabel.setGeometry(QRect(20, 20, 91, 16))
        self.listPushButton = QPushButton(Form)
        self.listPushButton.setObjectName(u"listPushButton")
        self.listPushButton.setGeometry(QRect(30, 190, 131, 32))
        self.quitPushButton = QPushButton(Form)
        self.quitPushButton.setObjectName(u"quitPushButton")
        self.quitPushButton.setGeometry(QRect(170, 190, 100, 32))
        self.debugPushButton = QPushButton(Form)
        self.debugPushButton.setObjectName(u"debugPushButton")
        self.debugPushButton.setGeometry(QRect(170, 150, 100, 32))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.createPushButton.setText(QCoreApplication.translate("Form", u"Create Ramdisk", None))
        self.mountLabel.setText(QCoreApplication.translate("Form", u"Mount Point", None))
        self.randomRadioButton.setText(QCoreApplication.translate("Form", u"Randomized", None))
        self.sizeLabel.setText(QCoreApplication.translate("Form", u"Ramdisk Size", None))
        self.listPushButton.setText(QCoreApplication.translate("Form", u"List Ramdisks", None))
        self.quitPushButton.setText(QCoreApplication.translate("Form", u"Quit", None))
        self.debugPushButton.setText(QCoreApplication.translate("Form", u"Debug", None))
    # retranslateUi

