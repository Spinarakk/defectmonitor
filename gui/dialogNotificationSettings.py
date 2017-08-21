# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogNotificationSettings.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dialogNotificationSettings(object):
    def setupUi(self, dialogNotificationSettings):
        dialogNotificationSettings.setObjectName(_fromUtf8("dialogNotificationSettings"))
        dialogNotificationSettings.setWindowModality(QtCore.Qt.NonModal)
        dialogNotificationSettings.resize(331, 231)
        dialogNotificationSettings.setMinimumSize(QtCore.QSize(331, 231))
        dialogNotificationSettings.setMaximumSize(QtCore.QSize(331, 231))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogNotificationSettings.setWindowIcon(icon)
        dialogNotificationSettings.setModal(True)
        self.lineUsername = QtGui.QLineEdit(dialogNotificationSettings)
        self.lineUsername.setGeometry(QtCore.QRect(130, 10, 191, 26))
        self.lineUsername.setText(_fromUtf8(""))
        self.lineUsername.setMaxLength(52)
        self.lineUsername.setObjectName(_fromUtf8("lineUsername"))
        self.labelEmailAddress = QtGui.QLabel(dialogNotificationSettings)
        self.labelEmailAddress.setGeometry(QtCore.QRect(10, 44, 111, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelEmailAddress.setFont(font)
        self.labelEmailAddress.setObjectName(_fromUtf8("labelEmailAddress"))
        self.labelUsername = QtGui.QLabel(dialogNotificationSettings)
        self.labelUsername.setGeometry(QtCore.QRect(10, 10, 101, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelUsername.setFont(font)
        self.labelUsername.setObjectName(_fromUtf8("labelUsername"))
        self.buttonBox = QtGui.QDialogButtonBox(dialogNotificationSettings)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(190, 160, 131, 61))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lineEmailAddress = QtGui.QLineEdit(dialogNotificationSettings)
        self.lineEmailAddress.setGeometry(QtCore.QRect(130, 44, 191, 26))
        self.lineEmailAddress.setText(_fromUtf8(""))
        self.lineEmailAddress.setMaxLength(52)
        self.lineEmailAddress.setObjectName(_fromUtf8("lineEmailAddress"))
        self.groupNotifications = QtGui.QGroupBox(dialogNotificationSettings)
        self.groupNotifications.setGeometry(QtCore.QRect(10, 80, 171, 141))
        self.groupNotifications.setObjectName(_fromUtf8("groupNotifications"))
        self.layoutWidget = QtGui.QWidget(self.groupNotifications)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 10, 151, 130))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.checkAll = QtGui.QCheckBox(self.layoutWidget)
        self.checkAll.setObjectName(_fromUtf8("checkAll"))
        self.verticalLayout.addWidget(self.checkAll)
        self.checkMinor = QtGui.QCheckBox(self.layoutWidget)
        self.checkMinor.setObjectName(_fromUtf8("checkMinor"))
        self.verticalLayout.addWidget(self.checkMinor)
        self.checkMajor = QtGui.QCheckBox(self.layoutWidget)
        self.checkMajor.setObjectName(_fromUtf8("checkMajor"))
        self.verticalLayout.addWidget(self.checkMajor)
        self.checkFailure = QtGui.QCheckBox(self.layoutWidget)
        self.checkFailure.setObjectName(_fromUtf8("checkFailure"))
        self.verticalLayout.addWidget(self.checkFailure)
        self.checkError = QtGui.QCheckBox(self.layoutWidget)
        self.checkError.setObjectName(_fromUtf8("checkError"))
        self.verticalLayout.addWidget(self.checkError)
        self.buttonSendTestEmail = QtGui.QPushButton(dialogNotificationSettings)
        self.buttonSendTestEmail.setGeometry(QtCore.QRect(190, 80, 131, 27))
        self.buttonSendTestEmail.setObjectName(_fromUtf8("buttonSendTestEmail"))

        self.retranslateUi(dialogNotificationSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dialogNotificationSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dialogNotificationSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogNotificationSettings)

    def retranslateUi(self, dialogNotificationSettings):
        dialogNotificationSettings.setWindowTitle(_translate("dialogNotificationSettings", "Notification Settings", None))
        self.labelEmailAddress.setText(_translate("dialogNotificationSettings", "Email Address", None))
        self.labelUsername.setText(_translate("dialogNotificationSettings", "Username", None))
        self.groupNotifications.setTitle(_translate("dialogNotificationSettings", "Receive Notifications For:", None))
        self.checkAll.setText(_translate("dialogNotificationSettings", "All", None))
        self.checkMinor.setText(_translate("dialogNotificationSettings", "Minor Defects", None))
        self.checkMajor.setText(_translate("dialogNotificationSettings", "Major Defects", None))
        self.checkFailure.setText(_translate("dialogNotificationSettings", "Capture Failure", None))
        self.checkError.setText(_translate("dialogNotificationSettings", "Program Error", None))
        self.buttonSendTestEmail.setText(_translate("dialogNotificationSettings", "Send Test Email", None))

import icons_rc
