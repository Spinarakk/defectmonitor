# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogCameraCalibration.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogCameraCalibration(object):
    def setupUi(self, dialogCameraCalibration):
        dialogCameraCalibration.setObjectName("dialogCameraCalibration")
        dialogCameraCalibration.resize(347, 369)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogCameraCalibration.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(dialogCameraCalibration)
        self.gridLayout.setObjectName("gridLayout")
        self.pushBrowseHI = QtWidgets.QPushButton(dialogCameraCalibration)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushBrowseHI.sizePolicy().hasHeightForWidth())
        self.pushBrowseHI.setSizePolicy(sizePolicy)
        self.pushBrowseHI.setObjectName("pushBrowseHI")
        self.gridLayout.addWidget(self.pushBrowseHI, 3, 3, 1, 1)
        self.labelTestImage = QtWidgets.QLabel(dialogCameraCalibration)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelTestImage.setFont(font)
        self.labelTestImage.setObjectName("labelTestImage")
        self.gridLayout.addWidget(self.labelTestImage, 4, 0, 1, 1)
        self.pushBrowseTI = QtWidgets.QPushButton(dialogCameraCalibration)
        self.pushBrowseTI.setObjectName("pushBrowseTI")
        self.gridLayout.addWidget(self.pushBrowseTI, 4, 3, 1, 1)
        self.labelStatus = QtWidgets.QLabel(dialogCameraCalibration)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout.addWidget(self.labelStatus, 5, 0, 1, 4)
        self.lineHomographyImage = QtWidgets.QLineEdit(dialogCameraCalibration)
        self.lineHomographyImage.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.lineHomographyImage.setReadOnly(True)
        self.lineHomographyImage.setObjectName("lineHomographyImage")
        self.gridLayout.addWidget(self.lineHomographyImage, 3, 1, 1, 2)
        self.lineTestImage = QtWidgets.QLineEdit(dialogCameraCalibration)
        self.lineTestImage.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.lineTestImage.setReadOnly(True)
        self.lineTestImage.setObjectName("lineTestImage")
        self.gridLayout.addWidget(self.lineTestImage, 4, 1, 1, 2)
        self.listImages = QtWidgets.QListWidget(dialogCameraCalibration)
        self.listImages.setObjectName("listImages")
        self.gridLayout.addWidget(self.listImages, 2, 0, 1, 4)
        self.lineCalibrationFolder = QtWidgets.QLineEdit(dialogCameraCalibration)
        self.lineCalibrationFolder.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.lineCalibrationFolder.setReadOnly(True)
        self.lineCalibrationFolder.setObjectName("lineCalibrationFolder")
        self.gridLayout.addWidget(self.lineCalibrationFolder, 0, 0, 1, 3)
        self.pushBrowseF = QtWidgets.QPushButton(dialogCameraCalibration)
        self.pushBrowseF.setObjectName("pushBrowseF")
        self.gridLayout.addWidget(self.pushBrowseF, 0, 3, 1, 1)
        self.labelHomographyImage = QtWidgets.QLabel(dialogCameraCalibration)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelHomographyImage.sizePolicy().hasHeightForWidth())
        self.labelHomographyImage.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelHomographyImage.setFont(font)
        self.labelHomographyImage.setObjectName("labelHomographyImage")
        self.gridLayout.addWidget(self.labelHomographyImage, 3, 0, 1, 1)
        self.frameButtons = QtWidgets.QFrame(dialogCameraCalibration)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameButtons.sizePolicy().hasHeightForWidth())
        self.frameButtons.setSizePolicy(sizePolicy)
        self.frameButtons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameButtons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameButtons.setObjectName("frameButtons")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frameButtons)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushStart = QtWidgets.QPushButton(self.frameButtons)
        self.pushStart.setEnabled(False)
        self.pushStart.setObjectName("pushStart")
        self.horizontalLayout.addWidget(self.pushStart)
        self.pushResults = QtWidgets.QPushButton(self.frameButtons)
        self.pushResults.setObjectName("pushResults")
        self.horizontalLayout.addWidget(self.pushResults)
        self.pushSave = QtWidgets.QPushButton(self.frameButtons)
        self.pushSave.setEnabled(False)
        self.pushSave.setObjectName("pushSave")
        self.horizontalLayout.addWidget(self.pushSave)
        self.pushDone = QtWidgets.QPushButton(self.frameButtons)
        self.pushDone.setObjectName("pushDone")
        self.horizontalLayout.addWidget(self.pushDone)
        self.gridLayout.addWidget(self.frameButtons, 12, 0, 1, 4)
        self.labelImages = QtWidgets.QLabel(dialogCameraCalibration)
        self.labelImages.setObjectName("labelImages")
        self.gridLayout.addWidget(self.labelImages, 1, 0, 1, 4)
        self.checkApply = QtWidgets.QCheckBox(dialogCameraCalibration)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkApply.setFont(font)
        self.checkApply.setObjectName("checkApply")
        self.gridLayout.addWidget(self.checkApply, 11, 2, 1, 2)
        self.checkSaveU = QtWidgets.QCheckBox(dialogCameraCalibration)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkSaveU.setFont(font)
        self.checkSaveU.setObjectName("checkSaveU")
        self.gridLayout.addWidget(self.checkSaveU, 10, 2, 1, 2)
        self.checkSaveC = QtWidgets.QCheckBox(dialogCameraCalibration)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.checkSaveC.setFont(font)
        self.checkSaveC.setObjectName("checkSaveC")
        self.gridLayout.addWidget(self.checkSaveC, 9, 2, 1, 2)
        self.progressBar = QtWidgets.QProgressBar(dialogCameraCalibration)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 6, 0, 1, 4)
        self.labelCalibrationSettings = QtWidgets.QLabel(dialogCameraCalibration)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelCalibrationSettings.setFont(font)
        self.labelCalibrationSettings.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCalibrationSettings.setObjectName("labelCalibrationSettings")
        self.gridLayout.addWidget(self.labelCalibrationSettings, 7, 0, 1, 4)
        self.frameCalibrationSettings = QtWidgets.QFrame(dialogCameraCalibration)
        self.frameCalibrationSettings.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameCalibrationSettings.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCalibrationSettings.setObjectName("frameCalibrationSettings")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frameCalibrationSettings)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setVerticalSpacing(4)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelWidth = QtWidgets.QLabel(self.frameCalibrationSettings)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelWidth.setFont(font)
        self.labelWidth.setObjectName("labelWidth")
        self.gridLayout_2.addWidget(self.labelWidth, 0, 0, 1, 1)
        self.spinWidth = QtWidgets.QSpinBox(self.frameCalibrationSettings)
        self.spinWidth.setMinimum(1)
        self.spinWidth.setMaximum(20)
        self.spinWidth.setProperty("value", 9)
        self.spinWidth.setObjectName("spinWidth")
        self.gridLayout_2.addWidget(self.spinWidth, 0, 1, 1, 1)
        self.labelHeight = QtWidgets.QLabel(self.frameCalibrationSettings)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelHeight.setFont(font)
        self.labelHeight.setObjectName("labelHeight")
        self.gridLayout_2.addWidget(self.labelHeight, 1, 0, 1, 1)
        self.spinHeight = QtWidgets.QSpinBox(self.frameCalibrationSettings)
        self.spinHeight.setMinimum(1)
        self.spinHeight.setMaximum(20)
        self.spinHeight.setProperty("value", 7)
        self.spinHeight.setObjectName("spinHeight")
        self.gridLayout_2.addWidget(self.spinHeight, 1, 1, 1, 1)
        self.labelRatio = QtWidgets.QLabel(self.frameCalibrationSettings)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.labelRatio.setFont(font)
        self.labelRatio.setObjectName("labelRatio")
        self.gridLayout_2.addWidget(self.labelRatio, 2, 0, 1, 1)
        self.spinRatio = QtWidgets.QSpinBox(self.frameCalibrationSettings)
        self.spinRatio.setMinimum(1)
        self.spinRatio.setMaximum(4)
        self.spinRatio.setProperty("value", 2)
        self.spinRatio.setObjectName("spinRatio")
        self.gridLayout_2.addWidget(self.spinRatio, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.frameCalibrationSettings, 9, 0, 3, 2)

        self.retranslateUi(dialogCameraCalibration)
        self.pushDone.clicked.connect(dialogCameraCalibration.close)
        QtCore.QMetaObject.connectSlotsByName(dialogCameraCalibration)
        dialogCameraCalibration.setTabOrder(self.pushBrowseF, self.listImages)
        dialogCameraCalibration.setTabOrder(self.listImages, self.checkSaveC)
        dialogCameraCalibration.setTabOrder(self.checkSaveC, self.checkSaveU)
        dialogCameraCalibration.setTabOrder(self.checkSaveU, self.checkApply)

    def retranslateUi(self, dialogCameraCalibration):
        _translate = QtCore.QCoreApplication.translate
        dialogCameraCalibration.setWindowTitle(_translate("dialogCameraCalibration", "Camera Calibration"))
        self.pushBrowseHI.setText(_translate("dialogCameraCalibration", "Browse..."))
        self.labelTestImage.setToolTip(_translate("dialogCameraCalibration", "Select the image to be used to test the calculated calibration results."))
        self.labelTestImage.setText(_translate("dialogCameraCalibration", "Test Image"))
        self.pushBrowseTI.setText(_translate("dialogCameraCalibration", "Browse..."))
        self.labelStatus.setText(_translate("dialogCameraCalibration", "Waiting to start process."))
        self.pushBrowseF.setText(_translate("dialogCameraCalibration", "Browse..."))
        self.labelHomographyImage.setToolTip(_translate("dialogCameraCalibration", "Select the image to be used to calculate the homography image."))
        self.labelHomographyImage.setText(_translate("dialogCameraCalibration", "Homography"))
        self.pushStart.setText(_translate("dialogCameraCalibration", "Start"))
        self.pushResults.setText(_translate("dialogCameraCalibration", "View Results"))
        self.pushSave.setText(_translate("dialogCameraCalibration", "Save Results"))
        self.pushDone.setText(_translate("dialogCameraCalibration", "Done"))
        self.labelImages.setText(_translate("dialogCameraCalibration", "List of images:"))
        self.checkApply.setToolTip(_translate("dialogCameraCalibration", "Check to apply found camera matrix, distortion coefficient and homography matrix processing to the sample image."))
        self.checkApply.setText(_translate("dialogCameraCalibration", "Apply to Test Image"))
        self.checkSaveU.setToolTip(_translate("dialogCameraCalibration", "Check to save undistorted calibration images to the undistorted folder."))
        self.checkSaveU.setText(_translate("dialogCameraCalibration", "Save Undistorted Images"))
        self.checkSaveC.setToolTip(_translate("dialogCameraCalibration", "Check to save drawn chessboard corner calibration images to the corners folder."))
        self.checkSaveC.setText(_translate("dialogCameraCalibration", "Save Chessboard Images"))
        self.labelCalibrationSettings.setText(_translate("dialogCameraCalibration", "Calibration Settings"))
        self.labelWidth.setToolTip(_translate("dialogCameraCalibration", "Sets the number of square corners the width of the chessboard has."))
        self.labelWidth.setText(_translate("dialogCameraCalibration", "Chessboard Width"))
        self.spinWidth.setToolTip(_translate("dialogCameraCalibration", "1 - 20"))
        self.labelHeight.setToolTip(_translate("dialogCameraCalibration", "Sets the number of square corners the height of the chessboard has."))
        self.labelHeight.setText(_translate("dialogCameraCalibration", "Chessboard Height"))
        self.spinHeight.setToolTip(_translate("dialogCameraCalibration", "1 - 20"))
        self.labelRatio.setToolTip(_translate("dialogCameraCalibration", "Sets the downscaling ratio to use to speed up calibration."))
        self.labelRatio.setText(_translate("dialogCameraCalibration", "Downscaling Ratio"))
        self.spinRatio.setToolTip(_translate("dialogCameraCalibration", "1 - 4"))

import icons_rc
