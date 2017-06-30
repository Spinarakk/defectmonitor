# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogCameraSettings.ui'
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

class Ui_dialogCameraSettings(object):
    def setupUi(self, dialogCameraSettings):
        dialogCameraSettings.setObjectName(_fromUtf8("dialogCameraSettings"))
        dialogCameraSettings.setWindowModality(QtCore.Qt.NonModal)
        dialogCameraSettings.resize(425, 440)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogCameraSettings.setWindowIcon(icon)
        dialogCameraSettings.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(dialogCameraSettings)
        self.buttonBox.setGeometry(QtCore.QRect(240, 400, 171, 31))
        self.buttonBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.buttonApply = QtGui.QPushButton(dialogCameraSettings)
        self.buttonApply.setEnabled(False)
        self.buttonApply.setGeometry(QtCore.QRect(140, 400, 93, 28))
        self.buttonApply.setObjectName(_fromUtf8("buttonApply"))

        self.retranslateUi(dialogCameraSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dialogCameraSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dialogCameraSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogCameraSettings)

    def retranslateUi(self, dialogCameraSettings):
        dialogCameraSettings.setWindowTitle(_translate("dialogCameraSettings", "Camera Settings", None))
        self.buttonApply.setText(_translate("dialogCameraSettings", "Apply", None))

import icons_rc
