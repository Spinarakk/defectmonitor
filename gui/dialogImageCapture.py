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
        dialogImageCapture.resize(458, 281)
        dialogImageCapture.setMaximumSize(QtCore.QSize(458, 281))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogImageCapture.setWindowIcon(icon)
        dialogImageCapture.setModal(True)
        self.labelCameraStatus = QtGui.QLabel(dialogImageCapture)
        self.labelCameraStatus.setGeometry(QtCore.QRect(340, 162, 111, 28))
        self.labelCameraStatus.setFrameShape(QtGui.QFrame.Panel)
        self.labelCameraStatus.setFrameShadow(QtGui.QFrame.Sunken)
        self.labelCameraStatus.setLineWidth(2)
        self.labelCameraStatus.setMidLineWidth(0)
        self.labelCameraStatus.setText(_fromUtf8(""))
        self.labelCameraStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCameraStatus.setObjectName(_fromUtf8("labelCameraStatus"))
        self.buttonCheckCamera = QtGui.QPushButton(dialogImageCapture)
        self.buttonCheckCamera.setGeometry(QtCore.QRect(180, 162, 151, 28))
        self.buttonCheckCamera.setObjectName(_fromUtf8("buttonCheckCamera"))
        self.buttonCameraSettings = QtGui.QPushButton(dialogImageCapture)
        self.buttonCameraSettings.setGeometry(QtCore.QRect(10, 162, 161, 28))
        self.buttonCameraSettings.setObjectName(_fromUtf8("buttonCameraSettings"))
        self.textSaveLocation = QtGui.QTextBrowser(dialogImageCapture)
        self.textSaveLocation.setGeometry(QtCore.QRect(10, 126, 321, 28))
        self.textSaveLocation.setObjectName(_fromUtf8("textSaveLocation"))
        self.buttonBrowse = QtGui.QPushButton(dialogImageCapture)
        self.buttonBrowse.setGeometry(QtCore.QRect(340, 126, 111, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.labelSaveLocation = QtGui.QLabel(dialogImageCapture)
        self.labelSaveLocation.setGeometry(QtCore.QRect(10, 106, 141, 16))
        self.labelSaveLocation.setObjectName(_fromUtf8("labelSaveLocation"))
        self.labelInformation = QtGui.QLabel(dialogImageCapture)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 441, 91))
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName(_fromUtf8("labelInformation"))
        self.buttonDone = QtGui.QPushButton(dialogImageCapture)
        self.buttonDone.setGeometry(QtCore.QRect(340, 241, 111, 31))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.buttonCapture = QtGui.QPushButton(dialogImageCapture)
        self.buttonCapture.setEnabled(False)
        self.buttonCapture.setGeometry(QtCore.QRect(10, 198, 161, 58))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.buttonCapture.setFont(font)
        self.buttonCapture.setObjectName(_fromUtf8("buttonCapture"))
        self.buttonRun = QtGui.QPushButton(dialogImageCapture)
        self.buttonRun.setEnabled(False)
        self.buttonRun.setGeometry(QtCore.QRect(180, 198, 151, 28))
        self.buttonRun.setObjectName(_fromUtf8("buttonRun"))
        self.buttonStop = QtGui.QPushButton(dialogImageCapture)
        self.buttonStop.setEnabled(False)
        self.buttonStop.setGeometry(QtCore.QRect(180, 228, 151, 28))
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
        self.labelTimeElapsed.setGeometry(QtCore.QRect(350, 198, 101, 20))
        self.labelTimeElapsed.setObjectName(_fromUtf8("labelTimeElapsed"))
        self.labelTime = QtGui.QLabel(dialogImageCapture)
        self.labelTime.setGeometry(QtCore.QRect(350, 218, 101, 20))
        self.labelTime.setObjectName(_fromUtf8("labelTime"))
        self.labelStatusBar = QtGui.QLabel(dialogImageCapture)
        self.labelStatusBar.setGeometry(QtCore.QRect(10, 260, 321, 16))
        self.labelStatusBar.setObjectName(_fromUtf8("labelStatusBar"))

        self.retranslateUi(dialogImageCapture)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogImageCapture.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogImageCapture)

    def retranslateUi(self, dialogImageCapture):
        dialogImageCapture.setWindowTitle(_translate("dialogImageCapture", "Image Capture", None))
        self.buttonCheckCamera.setText(_translate("dialogImageCapture", "Check Camera", None))
        self.buttonCameraSettings.setText(_translate("dialogImageCapture", "Camera Settings", None))
        self.buttonBrowse.setText(_translate("dialogImageCapture", "Browse", None))
        self.labelSaveLocation.setText(_translate("dialogImageCapture", "Save Location", None))
        self.labelInformation.setText(_translate("dialogImageCapture", "This tool allows the user to change camera settings and take images from the camera which are saved to the given location. Please check that a camera is available and browse to a save location before capturing images. Press Capture to take one picture. Press Run and run the 3D machine, where the magnetic trigger will take images as the machine completes the scan and coat processes.", None))
        self.buttonDone.setText(_translate("dialogImageCapture", "Done", None))
        self.buttonCapture.setText(_translate("dialogImageCapture", "Capture", None))
        self.buttonRun.setText(_translate("dialogImageCapture", "Run", None))
        self.buttonStop.setText(_translate("dialogImageCapture", "Stop", None))
        self.labelTimeElapsed.setText(_translate("dialogImageCapture", "Time Elapsed:", None))
        self.labelTime.setText(_translate("dialogImageCapture", "00:00:00", None))
        self.labelStatusBar.setText(_translate("dialogImageCapture", "Status:", None))

import icons_rc
