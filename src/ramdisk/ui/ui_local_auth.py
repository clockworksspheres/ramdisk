# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'local_auth.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QSizePolicy, QWidget)

class Ui_LocalAuth(object):
    def setupUi(self, LocalAuth):
        if not LocalAuth.objectName():
            LocalAuth.setObjectName(u"LocalAuth")
        LocalAuth.resize(337, 206)
        self.buttonBox = QDialogButtonBox(LocalAuth)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(10, 150, 301, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.titleLabel = QLabel(LocalAuth)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setGeometry(QRect(100, 10, 131, 16))
        self.usernameLabel = QLabel(LocalAuth)
        self.usernameLabel.setObjectName(u"usernameLabel")
        self.usernameLabel.setGeometry(QRect(30, 30, 81, 16))
        self.passwordLabel = QLabel(LocalAuth)
        self.passwordLabel.setObjectName(u"passwordLabel")
        self.passwordLabel.setGeometry(QRect(30, 90, 58, 16))
        self.userLineEdit = QLineEdit(LocalAuth)
        self.userLineEdit.setObjectName(u"userLineEdit")
        self.userLineEdit.setGeometry(QRect(30, 50, 151, 21))
        self.passLineEdit = QLineEdit(LocalAuth)
        self.passLineEdit.setObjectName(u"passLineEdit")
        self.passLineEdit.setGeometry(QRect(30, 110, 161, 21))
        self.passLineEdit.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.retranslateUi(LocalAuth)
        self.buttonBox.accepted.connect(LocalAuth.accept)
        self.buttonBox.rejected.connect(LocalAuth.reject)

        QMetaObject.connectSlotsByName(LocalAuth)
    # setupUi

    def retranslateUi(self, LocalAuth):
        LocalAuth.setWindowTitle(QCoreApplication.translate("LocalAuth", u"Dialog", None))
        self.titleLabel.setText(QCoreApplication.translate("LocalAuth", u"Local Authentication", None))
        self.usernameLabel.setText(QCoreApplication.translate("LocalAuth", u"Username", None))
        self.passwordLabel.setText(QCoreApplication.translate("LocalAuth", u"Password", None))
    # retranslateUi

