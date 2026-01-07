# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'local_auth_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialogButtonBox, QLabel,
    QLineEdit, QSizePolicy, QWidget)

class Ui_LocalAuth(object):
    def setupUi(self, LocalAuth):
        if not LocalAuth.objectName():
            LocalAuth.setObjectName(u"LocalAuth")
        LocalAuth.resize(247, 243)
        LocalAuth.setWindowOpacity(20.000000000000000)
        LocalAuth.setAutoFillBackground(False)
        LocalAuth.setStyleSheet(u"QWidget {\n"
"	background-color: #ADADAD;\n"
"}")
        self.buttonBox = QDialogButtonBox(LocalAuth)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(70, 170, 131, 41))
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.userLineEdit = QLineEdit(LocalAuth)
        self.userLineEdit.setObjectName(u"userLineEdit")
        self.userLineEdit.setGeometry(QRect(30, 70, 161, 21))
        self.userLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border-style: outset;\n"
"	background-color: #e6e6e6;\n"
"    font: 12px black;\n"
"}")
        self.passLineEdit = QLineEdit(LocalAuth)
        self.passLineEdit.setObjectName(u"passLineEdit")
        self.passLineEdit.setGeometry(QRect(30, 130, 161, 21))
        self.passLineEdit.setStyleSheet(u"QLineEdit {\n"
"    border-style: outset;\n"
"	background-color: #e6e6e6;\n"
"    font: 12px black;\n"
"}")
        self.passLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.titleLabel = QLabel(LocalAuth)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setGeometry(QRect(30, 10, 151, 21))
        self.titleLabel.setStyleSheet(u"QLabel {\n"
"    font-weight: bold;\n"
"    color: black;\n"
"}")
        self.userLabel = QLabel(LocalAuth)
        self.userLabel.setObjectName(u"userLabel")
        self.userLabel.setGeometry(QRect(30, 46, 91, 20))
        self.userLabel.setStyleSheet(u"")
        self.passLabel = QLabel(LocalAuth)
        self.passLabel.setObjectName(u"passLabel")
        self.passLabel.setGeometry(QRect(30, 106, 91, 20))
        self.passLabel.setAutoFillBackground(False)
        self.passLabel.setStyleSheet(u"")

        self.retranslateUi(LocalAuth)

        QMetaObject.connectSlotsByName(LocalAuth)
    # setupUi

    def retranslateUi(self, LocalAuth):
        LocalAuth.setWindowTitle(QCoreApplication.translate("LocalAuth", u"Form", None))
        self.userLineEdit.setText("")
        self.passLineEdit.setText("")
        self.titleLabel.setText(QCoreApplication.translate("LocalAuth", u"Local Authentication", None))
        self.userLabel.setText(QCoreApplication.translate("LocalAuth", u"Username", None))
        self.passLabel.setText(QCoreApplication.translate("LocalAuth", u"Password", None))
    # retranslateUi

