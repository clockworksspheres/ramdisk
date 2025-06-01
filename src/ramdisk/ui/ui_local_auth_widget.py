# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'local_auth_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
        LocalAuth.resize(228, 242)
        self.buttonBox = QDialogButtonBox(LocalAuth)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(40, 180, 152, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.userLineEdit = QLineEdit(LocalAuth)
        self.userLineEdit.setObjectName(u"userLineEdit")
        self.userLineEdit.setGeometry(QRect(30, 70, 161, 21))
        self.passLineEdit = QLineEdit(LocalAuth)
        self.passLineEdit.setObjectName(u"passLineEdit")
        self.passLineEdit.setGeometry(QRect(30, 130, 161, 21))
        self.passLineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.titleLabel = QLabel(LocalAuth)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setGeometry(QRect(30, 10, 151, 16))
        self.userLabel = QLabel(LocalAuth)
        self.userLabel.setObjectName(u"userLabel")
        self.userLabel.setGeometry(QRect(30, 50, 81, 16))
        self.passLabel = QLabel(LocalAuth)
        self.passLabel.setObjectName(u"passLabel")
        self.passLabel.setGeometry(QRect(30, 110, 81, 16))

        self.retranslateUi(LocalAuth)

        QMetaObject.connectSlotsByName(LocalAuth)
    # setupUi

    def retranslateUi(self, LocalAuth):
        LocalAuth.setWindowTitle(QCoreApplication.translate("LocalAuth", u"Form", None))
        self.titleLabel.setText(QCoreApplication.translate("LocalAuth", u"Local Authentication", None))
        self.userLabel.setText(QCoreApplication.translate("LocalAuth", u"Username", None))
        self.passLabel.setText(QCoreApplication.translate("LocalAuth", u"Password", None))
    # retranslateUi

