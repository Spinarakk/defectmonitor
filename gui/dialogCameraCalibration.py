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
        dialogCameraCalibration.resize(411, 476)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogCameraCalibration.setWindowIcon(icon)
        dialogCameraCalibration.setModal(True)
        self.labelInformation1 = QtGui.QLabel(dialogCameraCalibration)
        self.labelInformation1.setGeometry(QtCore.QRect(10, 10, 391, 81))
        self.labelInformation1.setScaledContents(False)
        self.labelInformation1.setWordWrap(True)
        self.labelInformation1.setObjectName(_fromUtf8("labelInformation1"))
        self.buttonBrowse = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonBrowse.setGeometry(QtCore.QRect(310, 99, 91, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.buttonStartCalibration = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonStartCalibration.setEnabled(False)
        self.buttonStartCalibration.setGeometry(QtCore.QRect(210, 404, 191, 28))
        self.buttonStartCalibration.setObjectName(_fromUtf8("buttonStartCalibration"))
        self.buttonDone = QtGui.QPushButton(dialogCameraCalibration)
        self.buttonDone.setGeometry(QtCore.QRect(210, 438, 191, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.progressBar = QtGui.QProgressBar(dialogCameraCalibration)
        self.progressBar.setGeometry(QtCore.QRect(210, 370, 191, 28))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.labelStatus = QtGui.QLabel(dialogCameraCalibration)
        self.labelStatus.setGeometry(QtCore.QRect(210, 336, 191, 28))
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.labelImages = QtGui.QLabel(dialogCameraCalibration)
        self.labelImages.setGeometry(QtCore.QRect(10, 130, 221, 21))
        self.labelImages.setObjectName(_fromUtf8("labelImages"))
        self.listImages = QtGui.QListWidget(dialogCameraCalibration)
        self.listImages.setGeometry(QtCore.QRect(10, 150, 391, 181))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.listImages.setFont(font)
        self.listImages.setObjectName(_fromUtf8("listImages"))
        self.label1 = QtGui.QLabel(dialogCameraCalibration)
        self.label1.setGeometry(QtCore.QRect(11, 336, 191, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label1.setFont(font)
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.label1.setObjectName(_fromUtf8("label1"))
        self.label2 = QtGui.QLabel(dialogCameraCalibration)
        self.label2.setGeometry(QtCore.QRect(11, 370, 141, 28))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label2.setFont(font)
        self.label2.setObjectName(_fromUtf8("label2"))
        self.label3 = QtGui.QLabel(dialogCameraCalibration)
        self.label3.setGeometry(QtCore.QRect(11, 404, 141, 28))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label3.setFont(font)
        self.label3.setObjectName(_fromUtf8("label3"))
        self.label4 = QtGui.QLabel(dialogCameraCalibration)
        self.label4.setGeometry(QtCore.QRect(11, 438, 141, 28))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label4.setFont(font)
        self.label4.setObjectName(_fromUtf8("label4"))
        self.spinWidth = QtGui.QSpinBox(dialogCameraCalibration)
        self.spinWidth.setGeometry(QtCore.QRect(160, 371, 41, 26))
        self.spinWidth.setMinimum(1)
        self.spinWidth.setMaximum(12)
        self.spinWidth.setProperty("value", 9)
        self.spinWidth.setObjectName(_fromUtf8("spinWidth"))
        self.spinHeight = QtGui.QSpinBox(dialogCameraCalibration)
        self.spinHeight.setGeometry(QtCore.QRect(160, 405, 41, 26))
        self.spinHeight.setMinimum(1)
        self.spinHeight.setMaximum(12)
        self.spinHeight.setProperty("value", 7)
        self.spinHeight.setObjectName(_fromUtf8("spinHeight"))
        self.spinRatio = QtGui.QSpinBox(dialogCameraCalibration)
        self.spinRatio.setGeometry(QtCore.QRect(160, 439, 41, 26))
        self.spinRatio.setMinimum(1)
        self.spinRatio.setMaximum(4)
        self.spinRatio.setProperty("value", 2)
        self.spinRatio.setObjectName(_fromUtf8("spinRatio"))
        self.lineCalibrationFolder = QtGui.QLineEdit(dialogCameraCalibration)
        self.lineCalibrationFolder.setGeometry(QtCore.QRect(10, 100, 291, 26))
        self.lineCalibrationFolder.setReadOnly(True)
        self.lineCalibrationFolder.setObjectName(_fromUtf8("lineCalibrationFolder"))

        self.retranslateUi(dialogCameraCalibration)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogCameraCalibration.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogCameraCalibration)

    def retranslateUi(self, dialogCameraCalibration):
        dialogCameraCalibration.setWindowTitle(_translate("dialogCameraCalibration", "Camera Calibration", None))
        self.labelInformation1.setText(_translate("dialogCameraCalibration", "To calibrate the camera, please select the folder containing your checkboard images. To determine the most accurate camera parameters, please provide at least 10 images. Calibration images must contain the word \"calibration_image\" in the file name, and will be displayed below.", None))
        self.buttonBrowse.setText(_translate("dialogCameraCalibration", "Browse...", None))
        self.buttonStartCalibration.setText(_translate("dialogCameraCalibration", "Start Calibration", None))
        self.buttonDone.setText(_translate("dialogCameraCalibration", "Done", None))
        self.labelStatus.setText(_translate("dialogCameraCalibration", "Waiting to start process.", None))
        self.labelImages.setText(_translate("dialogCameraCalibration", "List of images:", None))
        self.label1.setText(_translate("dialogCameraCalibration", "Calibration Settings", None))
        self.label2.setToolTip(_translate("dialogCameraCalibration", "Sets the number of squares the width of the checkerboard has.", None))
        self.label2.setText(_translate("dialogCameraCalibration", "Checkerboard Width", None))
        self.label3.setToolTip(_translate("dialogCameraCalibration", "Sets the number of squares the height of the checkerboard has.", None))
        self.label3.setText(_translate("dialogCameraCalibration", "Checkerboard Height", None))
        self.label4.setToolTip(_translate("dialogCameraCalibration", "Sets the downscaling ratio to use to speed up calibration but reduce accuracy.", None))
        self.label4.setText(_translate("dialogCameraCalibration", "Downscaling Ratio", None))
        self.spinWidth.setToolTip(_translate("dialogCameraCalibration", "1 - 12", None))
        self.spinHeight.setToolTip(_translate("dialogCameraCalibration", "1 - 12", None))
        self.spinRatio.setToolTip(_translate("dialogCameraCalibration", "1 - 4", None))

import icons_rc
