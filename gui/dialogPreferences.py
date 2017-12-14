# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogPreferences.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogPreferences(object):
    def setupUi(self, dialogPreferences):
        dialogPreferences.setObjectName("dialogPreferences")
        dialogPreferences.resize(316, 287)
        self.gridLayout = QtWidgets.QGridLayout(dialogPreferences)
        self.gridLayout.setObjectName("gridLayout")
        self.frameBuildInfo = QtWidgets.QFrame(dialogPreferences)
        self.frameBuildInfo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameBuildInfo.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameBuildInfo.setObjectName("frameBuildInfo")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frameBuildInfo)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelBuildFolder = QtWidgets.QLabel(self.frameBuildInfo)
        self.labelBuildFolder.setObjectName("labelBuildFolder")
        self.horizontalLayout.addWidget(self.labelBuildFolder)
        self.lineBuildFolder = QtWidgets.QLineEdit(self.frameBuildInfo)
        self.lineBuildFolder.setReadOnly(True)
        self.lineBuildFolder.setObjectName("lineBuildFolder")
        self.horizontalLayout.addWidget(self.lineBuildFolder)
        self.pushBrowseBF = QtWidgets.QPushButton(self.frameBuildInfo)
        self.pushBrowseBF.setObjectName("pushBrowseBF")
        self.horizontalLayout.addWidget(self.pushBrowseBF)
        self.gridLayout.addWidget(self.frameBuildInfo, 0, 0, 1, 3)
        self.frameButtons = QtWidgets.QFrame(dialogPreferences)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameButtons.sizePolicy().hasHeightForWidth())
        self.frameButtons.setSizePolicy(sizePolicy)
        self.frameButtons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameButtons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameButtons.setObjectName("frameButtons")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frameButtons)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushApply = QtWidgets.QPushButton(self.frameButtons)
        self.pushApply.setEnabled(False)
        self.pushApply.setObjectName("pushApply")
        self.horizontalLayout_2.addWidget(self.pushApply)
        self.pushOK = QtWidgets.QPushButton(self.frameButtons)
        self.pushOK.setObjectName("pushOK")
        self.horizontalLayout_2.addWidget(self.pushOK)
        self.pushCancel = QtWidgets.QPushButton(self.frameButtons)
        self.pushCancel.setObjectName("pushCancel")
        self.horizontalLayout_2.addWidget(self.pushCancel)
        self.gridLayout.addWidget(self.frameButtons, 7, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(dialogPreferences)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setContentsMargins(9, 3, 9, 6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.labelThickness = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.labelThickness.setFont(font)
        self.labelThickness.setObjectName("labelThickness")
        self.gridLayout_2.addWidget(self.labelThickness, 1, 0, 1, 1)
        self.spinSize = QtWidgets.QSpinBox(self.groupBox)
        self.spinSize.setMinimum(5)
        self.spinSize.setMaximum(1205)
        self.spinSize.setSingleStep(5)
        self.spinSize.setObjectName("spinSize")
        self.gridLayout_2.addWidget(self.spinSize, 0, 1, 1, 1)
        self.spinThickness = QtWidgets.QSpinBox(self.groupBox)
        self.spinThickness.setMinimum(1)
        self.spinThickness.setMaximum(10)
        self.spinThickness.setObjectName("spinThickness")
        self.gridLayout_2.addWidget(self.spinThickness, 1, 1, 1, 1)
        self.labelSize = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.labelSize.setFont(font)
        self.labelSize.setObjectName("labelSize")
        self.gridLayout_2.addWidget(self.labelSize, 0, 0, 1, 1)
        self.pushModify = QtWidgets.QPushButton(self.groupBox)
        self.pushModify.setObjectName("pushModify")
        self.gridLayout_2.addWidget(self.pushModify, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 3, 0, 1, 1)
        self.groupBuildDefaults = QtWidgets.QGroupBox(dialogPreferences)
        self.groupBuildDefaults.setObjectName("groupBuildDefaults")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBuildDefaults)
        self.gridLayout_3.setContentsMargins(-1, 3, -1, 6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lineBuildName = QtWidgets.QLineEdit(self.groupBuildDefaults)
        self.lineBuildName.setClearButtonEnabled(True)
        self.lineBuildName.setObjectName("lineBuildName")
        self.gridLayout_3.addWidget(self.lineBuildName, 1, 1, 1, 1)
        self.labelBuildName = QtWidgets.QLabel(self.groupBuildDefaults)
        self.labelBuildName.setObjectName("labelBuildName")
        self.gridLayout_3.addWidget(self.labelBuildName, 1, 0, 1, 1)
        self.labelUsername = QtWidgets.QLabel(self.groupBuildDefaults)
        self.labelUsername.setObjectName("labelUsername")
        self.gridLayout_3.addWidget(self.labelUsername, 2, 0, 1, 1)
        self.labelEmailAddress = QtWidgets.QLabel(self.groupBuildDefaults)
        self.labelEmailAddress.setObjectName("labelEmailAddress")
        self.gridLayout_3.addWidget(self.labelEmailAddress, 3, 0, 1, 1)
        self.lineEmailAddress = QtWidgets.QLineEdit(self.groupBuildDefaults)
        self.lineEmailAddress.setClearButtonEnabled(True)
        self.lineEmailAddress.setObjectName("lineEmailAddress")
        self.gridLayout_3.addWidget(self.lineEmailAddress, 3, 1, 1, 1)
        self.lineUsername = QtWidgets.QLineEdit(self.groupBuildDefaults)
        self.lineUsername.setClearButtonEnabled(True)
        self.lineUsername.setObjectName("lineUsername")
        self.gridLayout_3.addWidget(self.lineUsername, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBuildDefaults, 5, 0, 1, 3)

        self.retranslateUi(dialogPreferences)
        self.pushCancel.clicked.connect(dialogPreferences.close)
        self.pushOK.clicked.connect(dialogPreferences.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogPreferences)
        dialogPreferences.setTabOrder(self.spinSize, self.spinThickness)
        dialogPreferences.setTabOrder(self.spinThickness, self.pushModify)

    def retranslateUi(self, dialogPreferences):
        _translate = QtCore.QCoreApplication.translate
        dialogPreferences.setWindowTitle(_translate("dialogPreferences", "Preferences"))
        self.labelBuildFolder.setText(_translate("dialogPreferences", "Build Folder"))
        self.pushBrowseBF.setText(_translate("dialogPreferences", "Browse..."))
        self.pushApply.setText(_translate("dialogPreferences", "Apply"))
        self.pushOK.setText(_translate("dialogPreferences", "OK"))
        self.pushCancel.setText(_translate("dialogPreferences", "Cancel"))
        self.groupBox.setTitle(_translate("dialogPreferences", "Gridline Settings"))
        self.labelThickness.setText(_translate("dialogPreferences", "Gridline Thickness"))
        self.spinSize.setToolTip(_translate("dialogPreferences", "5 - 1205"))
        self.spinThickness.setToolTip(_translate("dialogPreferences", "1 - 10"))
        self.labelSize.setText(_translate("dialogPreferences", "Grid Size (Pixels)"))
        self.pushModify.setText(_translate("dialogPreferences", "Modify"))
        self.groupBuildDefaults.setTitle(_translate("dialogPreferences", "Build Defaults"))
        self.labelBuildName.setText(_translate("dialogPreferences", "Build Name"))
        self.labelUsername.setText(_translate("dialogPreferences", "Username"))
        self.labelEmailAddress.setText(_translate("dialogPreferences", "Email Address"))

