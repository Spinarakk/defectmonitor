# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogNewBuild.ui'
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

class Ui_dialogNewBuild(object):
    def setupUi(self, dialogNewBuild):
        dialogNewBuild.setObjectName(_fromUtf8("dialogNewBuild"))
        dialogNewBuild.setWindowModality(QtCore.Qt.ApplicationModal)
        dialogNewBuild.resize(400, 194)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogNewBuild.setWindowIcon(icon)
        self.buttonBox = QtGui.QDialogButtonBox(dialogNewBuild)
        self.buttonBox.setGeometry(QtCore.QRect(300, 120, 81, 61))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lineBuildName = QtGui.QLineEdit(dialogNewBuild)
        self.lineBuildName.setGeometry(QtCore.QRect(130, 10, 131, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineBuildName.sizePolicy().hasHeightForWidth())
        self.lineBuildName.setSizePolicy(sizePolicy)
        self.lineBuildName.setText(_fromUtf8(""))
        self.lineBuildName.setMaxLength(30)
        self.lineBuildName.setObjectName(_fromUtf8("lineBuildName"))
        self.labelBuildName = QtGui.QLabel(dialogNewBuild)
        self.labelBuildName.setGeometry(QtCore.QRect(10, 10, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelBuildName.setFont(font)
        self.labelBuildName.setObjectName(_fromUtf8("labelBuildName"))
        self.comboPlatform = QtGui.QComboBox(dialogNewBuild)
        self.comboPlatform.setGeometry(QtCore.QRect(130, 40, 251, 22))
        self.comboPlatform.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.comboPlatform.setObjectName(_fromUtf8("comboPlatform"))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.labelBuildPlatform = QtGui.QLabel(dialogNewBuild)
        self.labelBuildPlatform.setGeometry(QtCore.QRect(10, 40, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelBuildPlatform.setFont(font)
        self.labelBuildPlatform.setObjectName(_fromUtf8("labelBuildPlatform"))
        self.line = QtGui.QFrame(dialogNewBuild)
        self.line.setGeometry(QtCore.QRect(10, 60, 381, 16))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.toolChangeDirectory = QtGui.QToolButton(dialogNewBuild)
        self.toolChangeDirectory.setGeometry(QtCore.QRect(270, 10, 111, 21))
        self.toolChangeDirectory.setToolTip(_fromUtf8(""))
        self.toolChangeDirectory.setStatusTip(_fromUtf8(""))
        self.toolChangeDirectory.setObjectName(_fromUtf8("toolChangeDirectory"))
        self.NoticeBox = QtGui.QGroupBox(dialogNewBuild)
        self.NoticeBox.setGeometry(QtCore.QRect(10, 80, 271, 111))
        self.NoticeBox.setObjectName(_fromUtf8("NoticeBox"))
        self.buttonUseLast = QtGui.QPushButton(self.NoticeBox)
        self.buttonUseLast.setGeometry(QtCore.QRect(190, 80, 75, 23))
        self.buttonUseLast.setObjectName(_fromUtf8("buttonUseLast"))
        self.labelEmail = QtGui.QLabel(self.NoticeBox)
        self.labelEmail.setGeometry(QtCore.QRect(10, 20, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelEmail.setFont(font)
        self.labelEmail.setObjectName(_fromUtf8("labelEmail"))
        self.lineEmail = QtGui.QLineEdit(self.NoticeBox)
        self.lineEmail.setGeometry(QtCore.QRect(120, 20, 141, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEmail.sizePolicy().hasHeightForWidth())
        self.lineEmail.setSizePolicy(sizePolicy)
        self.lineEmail.setText(_fromUtf8(""))
        self.lineEmail.setMaxLength(100)
        self.lineEmail.setObjectName(_fromUtf8("lineEmail"))
        self.linePassword = QtGui.QLineEdit(self.NoticeBox)
        self.linePassword.setGeometry(QtCore.QRect(120, 50, 141, 20))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.linePassword.sizePolicy().hasHeightForWidth())
        self.linePassword.setSizePolicy(sizePolicy)
        self.linePassword.setInputMask(_fromUtf8(""))
        self.linePassword.setText(_fromUtf8(""))
        self.linePassword.setMaxLength(24)
        self.linePassword.setFrame(True)
        self.linePassword.setEchoMode(QtGui.QLineEdit.Password)
        self.linePassword.setPlaceholderText(_fromUtf8(""))
        self.linePassword.setObjectName(_fromUtf8("linePassword"))
        self.labelAccessCode = QtGui.QLabel(self.NoticeBox)
        self.labelAccessCode.setGeometry(QtCore.QRect(10, 50, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelAccessCode.setFont(font)
        self.labelAccessCode.setObjectName(_fromUtf8("labelAccessCode"))
        self.buttonSetupFCM = QtGui.QPushButton(self.NoticeBox)
        self.buttonSetupFCM.setGeometry(QtCore.QRect(64, 80, 121, 23))
        self.buttonSetupFCM.setObjectName(_fromUtf8("buttonSetupFCM"))

        self.retranslateUi(dialogNewBuild)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dialogNewBuild.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dialogNewBuild.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogNewBuild)

    def retranslateUi(self, dialogNewBuild):
        dialogNewBuild.setWindowTitle(_translate("dialogNewBuild", "New Build", None))
        self.labelBuildName.setText(_translate("dialogNewBuild", "Build Name", None))
        self.comboPlatform.setItemText(0, _translate("dialogNewBuild", "Concept X1000R (636 x 406 mm)", None))
        self.comboPlatform.setItemText(1, _translate("dialogNewBuild", "Concept X2000R (800 x 400 mm)", None))
        self.comboPlatform.setItemText(2, _translate("dialogNewBuild", "EOS M280/M290 (250 x 250 mm)", None))
        self.labelBuildPlatform.setText(_translate("dialogNewBuild", "Build Platform", None))
        self.toolChangeDirectory.setText(_translate("dialogNewBuild", "Change Directory", None))
        self.NoticeBox.setTitle(_translate("dialogNewBuild", "Notification settings", None))
        self.buttonUseLast.setText(_translate("dialogNewBuild", "Use Last", None))
        self.labelEmail.setText(_translate("dialogNewBuild", "Email", None))
        self.labelAccessCode.setText(_translate("dialogNewBuild", "Access code", None))
        self.buttonSetupFCM.setText(_translate("dialogNewBuild", "Setup FCM", None))

import icons_rc