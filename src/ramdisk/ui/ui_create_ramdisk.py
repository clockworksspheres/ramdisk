# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'create_ramdisk.ui'
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
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setGeometry(QRect(180, 40, 51, 21))
        self.horizontalSlider = QSlider(Form)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setGeometry(QRect(10, 40, 160, 25))
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(30, 150, 131, 32))
        self.lineEdit_2 = QLineEdit(Form)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setGeometry(QRect(10, 100, 221, 21))
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 80, 81, 16))
        self.radioButton = QRadioButton(Form)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setGeometry(QRect(100, 80, 99, 20))
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(20, 20, 91, 16))
        self.pushButton_2 = QPushButton(Form)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(30, 190, 131, 32))
        self.pushButton_3 = QPushButton(Form)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(170, 190, 100, 32))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Create Ramdisk", None))
        self.label.setText(QCoreApplication.translate("Form", u"Mount Point", None))
        self.radioButton.setText(QCoreApplication.translate("Form", u"Randomized", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Ramdisk Size", None))
        self.pushButton_2.setText(QCoreApplication.translate("Form", u"List Ramdisks", None))
        self.pushButton_3.setText(QCoreApplication.translate("Form", u"Quit", None))
    # retranslateUi

