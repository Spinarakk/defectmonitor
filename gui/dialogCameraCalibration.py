# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogCameraCalibration.ui'
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

class Ui_dialogCameraCalibration(object):
    def setupUi(self, dialogCameraCalibration):
        dialogCameraCalibration.setObjectName(_fromUtf8("dialogCameraCalibration"))
        dialogCameraCalibration.resize(383, 441)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogCameraCalibration.setWindowIcon(icon)
        dialogCameraCalibration.setModal(True)
        self.labelInformation1 = QtGui.QLabel(dialogCameraCalibration)
        self.labelInformation1.setGeometry(QtCore.QRect(10, 10, 361, 51))
        self.labelInformation1.setScaledContents(False)
        self.labelInformation1.setWordWrap(True)
        self.labelInformation1.setObjectName(_fromUtf8("labelInformation1"))
        self.buttonBrowse = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonBrowse.setGeometry(QtCore.QRect(280, 100, 93, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.textFolderName = QtGui.QTextBrowser(dialogCameraCalibration)
        self.textFolderName.setGeometry(QtCore.QRect(10, 100, 261, 31))
        self.textFolderName.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textFolderName.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textFolderName.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.textFolderName.setObjectName(_fromUtf8("textFolderName"))
        self.buttonStartCalibration = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonStartCalibration.setEnabled(False)
        self.buttonStartCalibration.setGeometry(QtCore.QRect(10, 400, 261, 28))
        self.buttonStartCalibration.setObjectName(_fromUtf8("buttonStartCalibration"))
        self.buttonDone = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonDone.setGeometry(QtCore.QRect(280, 400, 93, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.progressBar = QtGui.QProgressBar(dialogCameraCalibration)
        self.progressBar.setGeometry(QtCore.QRect(10, 370, 361, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.labelProgress = QtGui.QLabel(dialogCameraCalibration)
        self.labelProgress.setGeometry(QtCore.QRect(10, 340, 361, 31))
        self.labelProgress.setAlignment(QtCore.Qt.AlignCenter)
        self.labelProgress.setObjectName(_fromUtf8("labelProgress"))
        self.labelInformation2 = QtGui.QLabel(dialogCameraCalibration)
        self.labelInformation2.setGeometry(QtCore.QRect(10, 60, 361, 31))
        self.labelInformation2.setWordWrap(True)
        self.labelInformation2.setObjectName(_fromUtf8("labelInformation2"))
        self.labelImages = QtGui.QLabel(dialogCameraCalibration)
        self.labelImages.setGeometry(QtCore.QRect(10, 140, 221, 16))
        self.labelImages.setObjectName(_fromUtf8("labelImages"))
        self.listImages = QtGui.QListWidget(dialogCameraCalibration)
        self.listImages.setGeometry(QtCore.QRect(10, 160, 361, 181))
        self.listImages.setObjectName(_fromUtf8("listImages"))

        self.retranslateUi(dialogCameraCalibration)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogCameraCalibration.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogCameraCalibration)

    def retranslateUi(self, dialogCameraCalibration):
        dialogCameraCalibration.setWindowTitle(_translate("dialogCameraCalibration", "Camera Calibration", None))
        self.labelInformation1.setText(_translate("dialogCameraCalibration", "To calibrate the camera, please select the folder containing your checkboard images. To determine the most accurate camera parameters, please provide at least 10 images.", None))
        self.buttonBrowse.setText(_translate("dialogCameraCalibration", "Browse...", None))
        self.buttonStartCalibration.setText(_translate("dialogCameraCalibration", "Start Calibration", None))
        self.buttonDone.setText(_translate("dialogCameraCalibration", "Done", None))
        self.labelProgress.setText(_translate("dialogCameraCalibration", "Waiting to start process.", None))
        self.labelInformation2.setText(_translate("dialogCameraCalibration", "Calibration images must contain the word \"calibration_image\" in the file name.", None))
        self.labelImages.setText(_translate("dialogCameraCalibration", "List of images:", None))

import icons_rc
