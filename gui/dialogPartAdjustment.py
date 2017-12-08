# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogPartAdjustment.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogPartAdjustment(object):
    def setupUi(self, dialogPartAdjustment):
        dialogPartAdjustment.setObjectName("dialogPartAdjustment")
        dialogPartAdjustment.resize(358, 290)
        self.gridLayout_3 = QtWidgets.QGridLayout(dialogPartAdjustment)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupRotationFlip = QtWidgets.QGroupBox(dialogPartAdjustment)
        self.groupRotationFlip.setObjectName("groupRotationFlip")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupRotationFlip)
        self.horizontalLayout.setContentsMargins(5, 3, 5, 3)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushRotateACW = QtWidgets.QPushButton(self.groupRotationFlip)
        self.pushRotateACW.setMinimumSize(QtCore.QSize(34, 34))
        self.pushRotateACW.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.pushRotateACW.setFont(font)
        self.pushRotateACW.setObjectName("pushRotateACW")
        self.horizontalLayout.addWidget(self.pushRotateACW)
        self.pushRotateCW = QtWidgets.QPushButton(self.groupRotationFlip)
        self.pushRotateCW.setMinimumSize(QtCore.QSize(34, 34))
        self.pushRotateCW.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushRotateCW.setFont(font)
        self.pushRotateCW.setObjectName("pushRotateCW")
        self.horizontalLayout.addWidget(self.pushRotateCW)
        self.pushFlipHorizontal = QtWidgets.QPushButton(self.groupRotationFlip)
        self.pushFlipHorizontal.setMinimumSize(QtCore.QSize(34, 34))
        self.pushFlipHorizontal.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushFlipHorizontal.setFont(font)
        self.pushFlipHorizontal.setObjectName("pushFlipHorizontal")
        self.horizontalLayout.addWidget(self.pushFlipHorizontal)
        self.pushFlipVertical = QtWidgets.QPushButton(self.groupRotationFlip)
        self.pushFlipVertical.setMinimumSize(QtCore.QSize(34, 34))
        self.pushFlipVertical.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushFlipVertical.setFont(font)
        self.pushFlipVertical.setObjectName("pushFlipVertical")
        self.horizontalLayout.addWidget(self.pushFlipVertical)
        self.gridLayout_3.addWidget(self.groupRotationFlip, 2, 2, 1, 2)
        self.groupValues = QtWidgets.QGroupBox(dialogPartAdjustment)
        self.groupValues.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.groupValues.setFont(font)
        self.groupValues.setObjectName("groupValues")
        self.gridLayout = QtWidgets.QGridLayout(self.groupValues)
        self.gridLayout.setContentsMargins(9, 3, 9, 6)
        self.gridLayout.setObjectName("gridLayout")
        self.labelPixels = QtWidgets.QLabel(self.groupValues)
        self.labelPixels.setObjectName("labelPixels")
        self.gridLayout.addWidget(self.labelPixels, 0, 0, 1, 1)
        self.spinPixels = QtWidgets.QSpinBox(self.groupValues)
        self.spinPixels.setMinimum(1)
        self.spinPixels.setMaximum(5000)
        self.spinPixels.setObjectName("spinPixels")
        self.gridLayout.addWidget(self.spinPixels, 0, 1, 1, 1)
        self.spinDegrees = QtWidgets.QDoubleSpinBox(self.groupValues)
        self.spinDegrees.setMinimum(0.0)
        self.spinDegrees.setMaximum(360.0)
        self.spinDegrees.setProperty("value", 1.0)
        self.spinDegrees.setObjectName("spinDegrees")
        self.gridLayout.addWidget(self.spinDegrees, 1, 1, 1, 1)
        self.labelDegrees = QtWidgets.QLabel(self.groupValues)
        self.labelDegrees.setObjectName("labelDegrees")
        self.gridLayout.addWidget(self.labelDegrees, 1, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupValues, 0, 0, 1, 1)
        self.groupTranslation = QtWidgets.QGroupBox(dialogPartAdjustment)
        self.groupTranslation.setObjectName("groupTranslation")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupTranslation)
        self.gridLayout_2.setContentsMargins(5, 3, 5, 3)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushTranslateUp = QtWidgets.QPushButton(self.groupTranslation)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushTranslateUp.setFont(font)
        self.pushTranslateUp.setObjectName("pushTranslateUp")
        self.gridLayout_2.addWidget(self.pushTranslateUp, 0, 0, 1, 1)
        self.pushTranslateDown = QtWidgets.QPushButton(self.groupTranslation)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushTranslateDown.setFont(font)
        self.pushTranslateDown.setObjectName("pushTranslateDown")
        self.gridLayout_2.addWidget(self.pushTranslateDown, 1, 0, 1, 1)
        self.pushTranslateLeft = QtWidgets.QPushButton(self.groupTranslation)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushTranslateLeft.setFont(font)
        self.pushTranslateLeft.setObjectName("pushTranslateLeft")
        self.gridLayout_2.addWidget(self.pushTranslateLeft, 2, 0, 1, 1)
        self.pushTranslateRight = QtWidgets.QPushButton(self.groupTranslation)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushTranslateRight.setFont(font)
        self.pushTranslateRight.setObjectName("pushTranslateRight")
        self.gridLayout_2.addWidget(self.pushTranslateRight, 3, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupTranslation, 0, 3, 2, 1)
        self.groupGeneral = QtWidgets.QGroupBox(dialogPartAdjustment)
        self.groupGeneral.setObjectName("groupGeneral")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupGeneral)
        self.gridLayout_5.setContentsMargins(5, 3, 5, 3)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.pushReset = QtWidgets.QPushButton(self.groupGeneral)
        self.pushReset.setEnabled(True)
        self.pushReset.setMinimumSize(QtCore.QSize(34, 34))
        self.pushReset.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushReset.setFont(font)
        self.pushReset.setObjectName("pushReset")
        self.gridLayout_5.addWidget(self.pushReset, 0, 0, 1, 1)
        self.pushUndo = QtWidgets.QPushButton(self.groupGeneral)
        self.pushUndo.setMinimumSize(QtCore.QSize(34, 34))
        self.pushUndo.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushUndo.setFont(font)
        self.pushUndo.setObjectName("pushUndo")
        self.gridLayout_5.addWidget(self.pushUndo, 0, 1, 1, 1)
        self.pushSave = QtWidgets.QPushButton(self.groupGeneral)
        self.pushSave.setMinimumSize(QtCore.QSize(34, 34))
        self.pushSave.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.pushSave.setFont(font)
        self.pushSave.setObjectName("pushSave")
        self.gridLayout_5.addWidget(self.pushSave, 0, 2, 1, 1)
        self.gridLayout_3.addWidget(self.groupGeneral, 0, 1, 1, 2)
        self.groupStretchPull = QtWidgets.QGroupBox(dialogPartAdjustment)
        self.groupStretchPull.setObjectName("groupStretchPull")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupStretchPull)
        self.gridLayout_4.setContentsMargins(5, 3, 5, 3)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.pushStretchLeftUp = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchLeftUp.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchLeftUp.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchLeftUp.setFont(font)
        self.pushStretchLeftUp.setObjectName("pushStretchLeftUp")
        self.gridLayout_4.addWidget(self.pushStretchLeftUp, 0, 1, 1, 1)
        self.pushStretchRightUp = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchRightUp.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchRightUp.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchRightUp.setFont(font)
        self.pushStretchRightUp.setCheckable(False)
        self.pushStretchRightUp.setObjectName("pushStretchRightUp")
        self.gridLayout_4.addWidget(self.pushStretchRightUp, 0, 3, 1, 1)
        self.pushStretchUpLeft = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchUpLeft.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchUpLeft.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchUpLeft.setFont(font)
        self.pushStretchUpLeft.setObjectName("pushStretchUpLeft")
        self.gridLayout_4.addWidget(self.pushStretchUpLeft, 1, 0, 1, 1)
        self.pushStretchNW = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchNW.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchNW.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchNW.setFont(font)
        self.pushStretchNW.setObjectName("pushStretchNW")
        self.gridLayout_4.addWidget(self.pushStretchNW, 1, 1, 1, 1)
        self.pushStretchN = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchN.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchN.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchN.setFont(font)
        self.pushStretchN.setObjectName("pushStretchN")
        self.gridLayout_4.addWidget(self.pushStretchN, 1, 2, 1, 1)
        self.pushStretchNE = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchNE.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchNE.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchNE.setFont(font)
        self.pushStretchNE.setObjectName("pushStretchNE")
        self.gridLayout_4.addWidget(self.pushStretchNE, 1, 3, 1, 1)
        self.pushStretchUpRight = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchUpRight.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchUpRight.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchUpRight.setFont(font)
        self.pushStretchUpRight.setObjectName("pushStretchUpRight")
        self.gridLayout_4.addWidget(self.pushStretchUpRight, 1, 4, 1, 1)
        self.pushStretchW = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchW.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchW.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchW.setFont(font)
        self.pushStretchW.setObjectName("pushStretchW")
        self.gridLayout_4.addWidget(self.pushStretchW, 2, 1, 1, 1)
        self.pushResetStretch = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushResetStretch.setMinimumSize(QtCore.QSize(34, 34))
        self.pushResetStretch.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushResetStretch.setFont(font)
        self.pushResetStretch.setObjectName("pushResetStretch")
        self.gridLayout_4.addWidget(self.pushResetStretch, 2, 2, 1, 1)
        self.pushStretchE = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchE.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchE.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchE.setFont(font)
        self.pushStretchE.setObjectName("pushStretchE")
        self.gridLayout_4.addWidget(self.pushStretchE, 2, 3, 1, 1)
        self.pushStretchDownLeft = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchDownLeft.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchDownLeft.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchDownLeft.setFont(font)
        self.pushStretchDownLeft.setObjectName("pushStretchDownLeft")
        self.gridLayout_4.addWidget(self.pushStretchDownLeft, 3, 0, 1, 1)
        self.pushStretchSW = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchSW.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchSW.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchSW.setFont(font)
        self.pushStretchSW.setObjectName("pushStretchSW")
        self.gridLayout_4.addWidget(self.pushStretchSW, 3, 1, 1, 1)
        self.pushStretchS = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchS.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchS.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchS.setFont(font)
        self.pushStretchS.setObjectName("pushStretchS")
        self.gridLayout_4.addWidget(self.pushStretchS, 3, 2, 1, 1)
        self.pushStretchSE = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchSE.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchSE.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchSE.setFont(font)
        self.pushStretchSE.setObjectName("pushStretchSE")
        self.gridLayout_4.addWidget(self.pushStretchSE, 3, 3, 1, 1)
        self.pushStretchDownRight = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchDownRight.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchDownRight.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchDownRight.setFont(font)
        self.pushStretchDownRight.setObjectName("pushStretchDownRight")
        self.gridLayout_4.addWidget(self.pushStretchDownRight, 3, 4, 1, 1)
        self.pushStretchLeftDown = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchLeftDown.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchLeftDown.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchLeftDown.setFont(font)
        self.pushStretchLeftDown.setObjectName("pushStretchLeftDown")
        self.gridLayout_4.addWidget(self.pushStretchLeftDown, 4, 1, 1, 1)
        self.pushStretchRightDown = QtWidgets.QPushButton(self.groupStretchPull)
        self.pushStretchRightDown.setMinimumSize(QtCore.QSize(34, 34))
        self.pushStretchRightDown.setMaximumSize(QtCore.QSize(34, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushStretchRightDown.setFont(font)
        self.pushStretchRightDown.setObjectName("pushStretchRightDown")
        self.gridLayout_4.addWidget(self.pushStretchRightDown, 4, 3, 1, 1)
        self.gridLayout_3.addWidget(self.groupStretchPull, 1, 0, 3, 2)
        self.pushDone = QtWidgets.QPushButton(dialogPartAdjustment)
        self.pushDone.setObjectName("pushDone")
        self.gridLayout_3.addWidget(self.pushDone, 3, 2, 1, 2)

        self.retranslateUi(dialogPartAdjustment)
        self.pushDone.clicked.connect(dialogPartAdjustment.close)
        QtCore.QMetaObject.connectSlotsByName(dialogPartAdjustment)
        dialogPartAdjustment.setTabOrder(self.pushDone, self.spinPixels)
        dialogPartAdjustment.setTabOrder(self.spinPixels, self.spinDegrees)
        dialogPartAdjustment.setTabOrder(self.spinDegrees, self.pushReset)
        dialogPartAdjustment.setTabOrder(self.pushReset, self.pushUndo)
        dialogPartAdjustment.setTabOrder(self.pushUndo, self.pushSave)
        dialogPartAdjustment.setTabOrder(self.pushSave, self.pushTranslateUp)
        dialogPartAdjustment.setTabOrder(self.pushTranslateUp, self.pushTranslateDown)
        dialogPartAdjustment.setTabOrder(self.pushTranslateDown, self.pushTranslateLeft)
        dialogPartAdjustment.setTabOrder(self.pushTranslateLeft, self.pushTranslateRight)
        dialogPartAdjustment.setTabOrder(self.pushTranslateRight, self.pushStretchLeftUp)
        dialogPartAdjustment.setTabOrder(self.pushStretchLeftUp, self.pushStretchRightUp)
        dialogPartAdjustment.setTabOrder(self.pushStretchRightUp, self.pushStretchUpLeft)
        dialogPartAdjustment.setTabOrder(self.pushStretchUpLeft, self.pushStretchNW)
        dialogPartAdjustment.setTabOrder(self.pushStretchNW, self.pushStretchN)
        dialogPartAdjustment.setTabOrder(self.pushStretchN, self.pushStretchNE)
        dialogPartAdjustment.setTabOrder(self.pushStretchNE, self.pushStretchUpRight)
        dialogPartAdjustment.setTabOrder(self.pushStretchUpRight, self.pushStretchW)
        dialogPartAdjustment.setTabOrder(self.pushStretchW, self.pushResetStretch)
        dialogPartAdjustment.setTabOrder(self.pushResetStretch, self.pushStretchE)
        dialogPartAdjustment.setTabOrder(self.pushStretchE, self.pushStretchDownLeft)
        dialogPartAdjustment.setTabOrder(self.pushStretchDownLeft, self.pushStretchSW)
        dialogPartAdjustment.setTabOrder(self.pushStretchSW, self.pushStretchS)
        dialogPartAdjustment.setTabOrder(self.pushStretchS, self.pushStretchSE)
        dialogPartAdjustment.setTabOrder(self.pushStretchSE, self.pushStretchDownRight)
        dialogPartAdjustment.setTabOrder(self.pushStretchDownRight, self.pushStretchLeftDown)
        dialogPartAdjustment.setTabOrder(self.pushStretchLeftDown, self.pushStretchRightDown)
        dialogPartAdjustment.setTabOrder(self.pushStretchRightDown, self.pushRotateACW)
        dialogPartAdjustment.setTabOrder(self.pushRotateACW, self.pushRotateCW)
        dialogPartAdjustment.setTabOrder(self.pushRotateCW, self.pushFlipHorizontal)
        dialogPartAdjustment.setTabOrder(self.pushFlipHorizontal, self.pushFlipVertical)

    def retranslateUi(self, dialogPartAdjustment):
        _translate = QtCore.QCoreApplication.translate
        dialogPartAdjustment.setWindowTitle(_translate("dialogPartAdjustment", "Part Adjustment"))
        self.groupRotationFlip.setTitle(_translate("dialogPartAdjustment", "Rotation / Flip"))
        self.pushRotateACW.setToolTip(_translate("dialogPartAdjustment", "Rotates the overlay anti-clockwise by the entered degrees."))
        self.pushRotateACW.setText(_translate("dialogPartAdjustment", "ACW"))
        self.pushRotateCW.setToolTip(_translate("dialogPartAdjustment", "Rotates the overlay clockwise by the entered degrees."))
        self.pushRotateCW.setText(_translate("dialogPartAdjustment", "CW"))
        self.pushFlipHorizontal.setToolTip(_translate("dialogPartAdjustment", "Flips the overlay along the horizontal axis."))
        self.pushFlipHorizontal.setText(_translate("dialogPartAdjustment", "H"))
        self.pushFlipVertical.setToolTip(_translate("dialogPartAdjustment", "Flips the overlay along the vertical axis."))
        self.pushFlipVertical.setText(_translate("dialogPartAdjustment", "V"))
        self.groupValues.setTitle(_translate("dialogPartAdjustment", "Values"))
        self.labelPixels.setText(_translate("dialogPartAdjustment", "Pixels"))
        self.labelDegrees.setText(_translate("dialogPartAdjustment", "Degrees"))
        self.groupTranslation.setTitle(_translate("dialogPartAdjustment", "Translation"))
        self.pushTranslateUp.setToolTip(_translate("dialogPartAdjustment", "Shifts the overlay up by the entered pixels."))
        self.pushTranslateUp.setText(_translate("dialogPartAdjustment", "UP"))
        self.pushTranslateDown.setToolTip(_translate("dialogPartAdjustment", "Shifts the overlay down by the entered pixels."))
        self.pushTranslateDown.setText(_translate("dialogPartAdjustment", "DOWN"))
        self.pushTranslateLeft.setToolTip(_translate("dialogPartAdjustment", "Shifts the overlay left by the entered pixels."))
        self.pushTranslateLeft.setText(_translate("dialogPartAdjustment", "LEFT"))
        self.pushTranslateRight.setToolTip(_translate("dialogPartAdjustment", "Shifts the overlay right by the entered pixels."))
        self.pushTranslateRight.setText(_translate("dialogPartAdjustment", "RIGHT"))
        self.groupGeneral.setTitle(_translate("dialogPartAdjustment", "General"))
        self.pushReset.setToolTip(_translate("dialogPartAdjustment", "Resets the overlay."))
        self.pushReset.setText(_translate("dialogPartAdjustment", "RE"))
        self.pushUndo.setToolTip(_translate("dialogPartAdjustment", "Undoes the most recent action."))
        self.pushUndo.setText(_translate("dialogPartAdjustment", "UN"))
        self.pushSave.setToolTip(_translate("dialogPartAdjustment", "Saves the current adjustment parameters to be used for part contour drawing."))
        self.pushSave.setText(_translate("dialogPartAdjustment", "SA"))
        self.groupStretchPull.setTitle(_translate("dialogPartAdjustment", "Stretch / Pull"))
        self.pushStretchLeftUp.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay up from the left by the entered pixels."))
        self.pushStretchLeftUp.setText(_translate("dialogPartAdjustment", "LU"))
        self.pushStretchRightUp.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay up from the right by the entered pixels."))
        self.pushStretchRightUp.setText(_translate("dialogPartAdjustment", "RU"))
        self.pushStretchUpLeft.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay left from the top by the entered pixels."))
        self.pushStretchUpLeft.setText(_translate("dialogPartAdjustment", "UL"))
        self.pushStretchNW.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay up-left by the entered pixels."))
        self.pushStretchNW.setText(_translate("dialogPartAdjustment", "NW"))
        self.pushStretchN.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay up by the entered pixels."))
        self.pushStretchN.setText(_translate("dialogPartAdjustment", "N"))
        self.pushStretchNE.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay up-right by the entered pixels."))
        self.pushStretchNE.setText(_translate("dialogPartAdjustment", "NE"))
        self.pushStretchUpRight.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay right from the top by the entered pixels."))
        self.pushStretchUpRight.setText(_translate("dialogPartAdjustment", "UR"))
        self.pushStretchW.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay left by the entered pixels."))
        self.pushStretchW.setText(_translate("dialogPartAdjustment", "W"))
        self.pushResetStretch.setToolTip(_translate("dialogPartAdjustment", "Resets any stretching or pulling of the overlay."))
        self.pushResetStretch.setText(_translate("dialogPartAdjustment", "RE"))
        self.pushStretchE.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay right by the entered pixels."))
        self.pushStretchE.setText(_translate("dialogPartAdjustment", "E"))
        self.pushStretchDownLeft.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay left from the bottom by the entered pixels."))
        self.pushStretchDownLeft.setText(_translate("dialogPartAdjustment", "DL"))
        self.pushStretchSW.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay down-left by the entered pixels."))
        self.pushStretchSW.setText(_translate("dialogPartAdjustment", "SW"))
        self.pushStretchS.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay down by the entered pixels."))
        self.pushStretchS.setText(_translate("dialogPartAdjustment", "S"))
        self.pushStretchSE.setToolTip(_translate("dialogPartAdjustment", "Stretches the overlay down-right by the entered pixels."))
        self.pushStretchSE.setText(_translate("dialogPartAdjustment", "SE"))
        self.pushStretchDownRight.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay right from the bottom by the entered pixels."))
        self.pushStretchDownRight.setText(_translate("dialogPartAdjustment", "DR"))
        self.pushStretchLeftDown.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay down from the left by the entered pixels."))
        self.pushStretchLeftDown.setText(_translate("dialogPartAdjustment", "LD"))
        self.pushStretchRightDown.setToolTip(_translate("dialogPartAdjustment", "Pulls the overlay down from the right by the entered pixels."))
        self.pushStretchRightDown.setText(_translate("dialogPartAdjustment", "RD"))
        self.pushDone.setText(_translate("dialogPartAdjustment", "Done"))

