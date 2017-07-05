# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogImageCapture.ui'
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

class Ui_dialogImageCapture(object):
    def setupUi(self, dialogImageCapture):
        dialogImageCapture.setObjectName(_fromUtf8("dialogImageCapture"))
        dialogImageCapture.setWindowModality(QtCore.Qt.NonModal)
        dialogImageCapture.resize(482, 309)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogImageCapture.setWindowIcon(icon)
        dialogImageCapture.setModal(True)
        self.labelCameraStatus = QtGui.QLabel(dialogImageCapture)
        self.labelCameraStatus.setGeometry(QtCore.QRect(330, 132, 141, 28))
        self.labelCameraStatus.setFrameShape(QtGui.QFrame.Panel)
        self.labelCameraStatus.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelCameraStatus.setLineWidth(2)
        self.labelCameraStatus.setMidLineWidth(0)
        self.labelCameraStatus.setText(_fromUtf8(""))
        self.labelCameraStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCameraStatus.setObjectName(_fromUtf8("labelCameraStatus"))
        self.buttonCheckCamera = QtGui.QPushButton(dialogImageCapture)
        self.buttonCheckCamera.setGeometry(QtCore.QRect(180, 132, 141, 28))
        self.buttonCheckCamera.setObjectName(_fromUtf8("buttonCheckCamera"))
        self.buttonCameraSettings = QtGui.QPushButton(dialogImageCapture)
        self.buttonCameraSettings.setGeometry(QtCore.QRect(10, 132, 161, 28))
        self.buttonCameraSettings.setObjectName(_fromUtf8("buttonCameraSettings"))
        self.textSaveLocation = QtGui.QTextBrowser(dialogImageCapture)
        self.textSaveLocation.setGeometry(QtCore.QRect(10, 96, 311, 28))
        self.textSaveLocation.setObjectName(_fromUtf8("textSaveLocation"))
        self.buttonBrowse = QtGui.QPushButton(dialogImageCapture)
        self.buttonBrowse.setGeometry(QtCore.QRect(330, 96, 141, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.labelSaveLocation = QtGui.QLabel(dialogImageCapture)
        self.labelSaveLocation.setGeometry(QtCore.QRect(10, 76, 141, 16))
        self.labelSaveLocation.setObjectName(_fromUtf8("labelSaveLocation"))
        self.labelInformation = QtGui.QLabel(dialogImageCapture)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 461, 61))
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName(_fromUtf8("labelInformation"))
        self.buttonDone = QtGui.QPushButton(dialogImageCapture)
        self.buttonDone.setGeometry(QtCore.QRect(330, 270, 141, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.buttonCapture = QtGui.QPushButton(dialogImageCapture)
        self.buttonCapture.setEnabled(False)
        self.buttonCapture.setGeometry(QtCore.QRect(10, 168, 161, 64))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.buttonCapture.setFont(font)
        self.buttonCapture.setObjectName(_fromUtf8("buttonCapture"))
        self.buttonRun = QtGui.QPushButton(dialogImageCapture)
        self.buttonRun.setEnabled(False)
        self.buttonRun.setGeometry(QtCore.QRect(180, 204, 141, 28))
        self.buttonRun.setObjectName(_fromUtf8("buttonRun"))
        self.buttonStop = QtGui.QPushButton(dialogImageCapture)
        self.buttonStop.setEnabled(False)
        self.buttonStop.setGeometry(QtCore.QRect(330, 204, 141, 28))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.buttonStop.setPalette(palette)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.buttonStop.setFont(font)
        self.buttonStop.setObjectName(_fromUtf8("buttonStop"))
        self.labelTimeElapsed = QtGui.QLabel(dialogImageCapture)
        self.labelTimeElapsed.setGeometry(QtCore.QRect(10, 238, 311, 20))
        self.labelTimeElapsed.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTimeElapsed.setObjectName(_fromUtf8("labelTimeElapsed"))
        self.labelStatusBar = QtGui.QLabel(dialogImageCapture)
        self.labelStatusBar.setGeometry(QtCore.QRect(10, 287, 321, 16))
        self.labelStatusBar.setObjectName(_fromUtf8("labelStatusBar"))
        self.progressBar = QtGui.QProgressBar(dialogImageCapture)
        self.progressBar.setGeometry(QtCore.QRect(10, 260, 311, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.checkApplyCorrection = QtGui.QCheckBox(dialogImageCapture)
        self.checkApplyCorrection.setGeometry(QtCore.QRect(340, 241, 131, 20))
        self.checkApplyCorrection.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkApplyCorrection.setObjectName(_fromUtf8("checkApplyCorrection"))
        self.labelTriggerStatus = QtGui.QLabel(dialogImageCapture)
        self.labelTriggerStatus.setGeometry(QtCore.QRect(330, 168, 141, 28))
        self.labelTriggerStatus.setFrameShape(QtGui.QFrame.Panel)
        self.labelTriggerStatus.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelTriggerStatus.setLineWidth(2)
        self.labelTriggerStatus.setMidLineWidth(0)
        self.labelTriggerStatus.setText(_fromUtf8(""))
        self.labelTriggerStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTriggerStatus.setObjectName(_fromUtf8("labelTriggerStatus"))
        self.buttonCheckTrigger = QtGui.QPushButton(dialogImageCapture)
        self.buttonCheckTrigger.setGeometry(QtCore.QRect(180, 168, 141, 28))
        self.buttonCheckTrigger.setObjectName(_fromUtf8("buttonCheckTrigger"))

        self.retranslateUi(dialogImageCapture)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogImageCapture.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogImageCapture)

    def retranslateUi(self, dialogImageCapture):
        dialogImageCapture.setWindowTitle(_translate("dialogImageCapture", "Image Capture", None))
        self.buttonCheckCamera.setText(_translate("dialogImageCapture", "Check Camera", None))
        self.buttonCameraSettings.setText(_translate("dialogImageCapture", "Camera Settings", None))
        self.buttonBrowse.setText(_translate("dialogImageCapture", "Browse", None))
        self.labelSaveLocation.setText(_translate("dialogImageCapture", "Save Location", None))
        self.labelInformation.setText(_translate("dialogImageCapture", "This tool allows the user to change camera settings and take images from the camera which are saved to the given location. To Capture individual images, please select a save location and check for an available camera. To Run using the hardware trigger, please also check for an available triggering device.", None))
        self.buttonDone.setText(_translate("dialogImageCapture", "Done", None))
        self.buttonCapture.setText(_translate("dialogImageCapture", "Capture", None))
        self.buttonRun.setText(_translate("dialogImageCapture", "Run", None))
        self.buttonStop.setText(_translate("dialogImageCapture", "Stop", None))
        self.labelTimeElapsed.setText(_translate("dialogImageCapture", "Time Elapsed: 00:00:00", None))
        self.labelStatusBar.setText(_translate("dialogImageCapture", "Status:", None))
        self.checkApplyCorrection.setText(_translate("dialogImageCapture", "Apply Correction", None))
        self.buttonCheckTrigger.setText(_translate("dialogImageCapture", "Check Trigger", None))

import icons_rc
