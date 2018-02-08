# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogPreferences.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogPreferences(object):
    def setupUi(self, dialogPreferences):
        dialogPreferences.setObjectName("dialogPreferences")
        dialogPreferences.resize(446, 373)
        self.gridLayout = QtWidgets.QGridLayout(dialogPreferences)
        self.gridLayout.setObjectName("gridLayout")
        self.groupSliceConverter = QtWidgets.QGroupBox(dialogPreferences)
        self.groupSliceConverter.setObjectName("groupSliceConverter")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupSliceConverter)
        self.gridLayout_4.setContentsMargins(-1, 3, -1, 6)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.labelCentrelineT = QtWidgets.QLabel(self.groupSliceConverter)
        self.labelCentrelineT.setObjectName("labelCentrelineT")
        self.gridLayout_4.addWidget(self.labelCentrelineT, 1, 1, 1, 1)
        self.spinContourT = QtWidgets.QSpinBox(self.groupSliceConverter)
        self.spinContourT.setMinimum(1)
        self.spinContourT.setMaximum(25)
        self.spinContourT.setObjectName("spinContourT")
        self.gridLayout_4.addWidget(self.spinContourT, 0, 2, 1, 1)
        self.labelContourT = QtWidgets.QLabel(self.groupSliceConverter)
        self.labelContourT.setObjectName("labelContourT")
        self.gridLayout_4.addWidget(self.labelContourT, 0, 1, 1, 1)
        self.spinCentrelineT = QtWidgets.QSpinBox(self.groupSliceConverter)
        self.spinCentrelineT.setMinimum(1)
        self.spinCentrelineT.setMaximum(25)
        self.spinCentrelineT.setObjectName("spinCentrelineT")
        self.gridLayout_4.addWidget(self.spinCentrelineT, 1, 2, 1, 1)
        self.labelROIOffset = QtWidgets.QLabel(self.groupSliceConverter)
        self.labelROIOffset.setObjectName("labelROIOffset")
        self.gridLayout_4.addWidget(self.labelROIOffset, 2, 1, 1, 1)
        self.spinROIOffset = QtWidgets.QSpinBox(self.groupSliceConverter)
        self.spinROIOffset.setMinimum(1)
        self.spinROIOffset.setMaximum(5000)
        self.spinROIOffset.setObjectName("spinROIOffset")
        self.gridLayout_4.addWidget(self.spinROIOffset, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.groupSliceConverter, 3, 1, 1, 2)
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
        self.gridLayout.addWidget(self.frameButtons, 7, 0, 1, 4)
        self.groupIdleTimeout = QtWidgets.QGroupBox(dialogPreferences)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupIdleTimeout.sizePolicy().hasHeightForWidth())
        self.groupIdleTimeout.setSizePolicy(sizePolicy)
        self.groupIdleTimeout.setObjectName("groupIdleTimeout")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupIdleTimeout)
        self.verticalLayout.setContentsMargins(-1, 3, -1, 6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelMinutes = QtWidgets.QLabel(self.groupIdleTimeout)
        self.labelMinutes.setAlignment(QtCore.Qt.AlignCenter)
        self.labelMinutes.setObjectName("labelMinutes")
        self.verticalLayout.addWidget(self.labelMinutes)
        self.spinIdleTimeout = QtWidgets.QSpinBox(self.groupIdleTimeout)
        self.spinIdleTimeout.setMinimum(0)
        self.spinIdleTimeout.setMaximum(180)
        self.spinIdleTimeout.setObjectName("spinIdleTimeout")
        self.verticalLayout.addWidget(self.spinIdleTimeout)
        self.gridLayout.addWidget(self.groupIdleTimeout, 3, 3, 1, 1)
        self.groupGridline = QtWidgets.QGroupBox(dialogPreferences)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupGridline.sizePolicy().hasHeightForWidth())
        self.groupGridline.setSizePolicy(sizePolicy)
        self.groupGridline.setObjectName("groupGridline")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupGridline)
        self.gridLayout_2.setContentsMargins(9, 3, 9, 6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spinThickness = QtWidgets.QSpinBox(self.groupGridline)
        self.spinThickness.setMinimum(1)
        self.spinThickness.setMaximum(10)
        self.spinThickness.setObjectName("spinThickness")
        self.gridLayout_2.addWidget(self.spinThickness, 1, 1, 1, 1)
        self.labelSize = QtWidgets.QLabel(self.groupGridline)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.labelSize.setFont(font)
        self.labelSize.setObjectName("labelSize")
        self.gridLayout_2.addWidget(self.labelSize, 0, 0, 1, 1)
        self.labelThickness = QtWidgets.QLabel(self.groupGridline)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.labelThickness.setFont(font)
        self.labelThickness.setObjectName("labelThickness")
        self.gridLayout_2.addWidget(self.labelThickness, 1, 0, 1, 1)
        self.spinSize = QtWidgets.QSpinBox(self.groupGridline)
        self.spinSize.setMinimum(5)
        self.spinSize.setMaximum(1205)
        self.spinSize.setSingleStep(5)
        self.spinSize.setObjectName("spinSize")
        self.gridLayout_2.addWidget(self.spinSize, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupGridline, 3, 0, 1, 1)
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
        self.gridLayout.addWidget(self.groupBuildDefaults, 5, 0, 1, 4)
        self.groupBox = QtWidgets.QGroupBox(dialogPreferences)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_5.setContentsMargins(-1, 3, -1, 6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.lineSenderAddress = QtWidgets.QLineEdit(self.groupBox)
        self.lineSenderAddress.setClearButtonEnabled(True)
        self.lineSenderAddress.setObjectName("lineSenderAddress")
        self.gridLayout_5.addWidget(self.lineSenderAddress, 1, 1, 1, 1)
        self.labelSenderAddress = QtWidgets.QLabel(self.groupBox)
        self.labelSenderAddress.setObjectName("labelSenderAddress")
        self.gridLayout_5.addWidget(self.labelSenderAddress, 1, 0, 1, 1)
        self.labelPassword = QtWidgets.QLabel(self.groupBox)
        self.labelPassword.setObjectName("labelPassword")
        self.gridLayout_5.addWidget(self.labelPassword, 2, 0, 1, 1)
        self.linePassword = QtWidgets.QLineEdit(self.groupBox)
        self.linePassword.setClearButtonEnabled(True)
        self.linePassword.setObjectName("linePassword")
        self.gridLayout_5.addWidget(self.linePassword, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.groupBox, 4, 0, 1, 4)
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
        self.gridLayout.addWidget(self.frameBuildInfo, 0, 0, 1, 5)

        self.retranslateUi(dialogPreferences)
        self.pushCancel.clicked.connect(dialogPreferences.close)
        self.pushOK.clicked.connect(dialogPreferences.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogPreferences)
        dialogPreferences.setTabOrder(self.lineBuildFolder, self.pushBrowseBF)
        dialogPreferences.setTabOrder(self.pushBrowseBF, self.spinSize)
        dialogPreferences.setTabOrder(self.spinSize, self.spinThickness)
        dialogPreferences.setTabOrder(self.spinThickness, self.spinContourT)
        dialogPreferences.setTabOrder(self.spinContourT, self.spinCentrelineT)
        dialogPreferences.setTabOrder(self.spinCentrelineT, self.spinROIOffset)
        dialogPreferences.setTabOrder(self.spinROIOffset, self.spinIdleTimeout)
        dialogPreferences.setTabOrder(self.spinIdleTimeout, self.lineSenderAddress)
        dialogPreferences.setTabOrder(self.lineSenderAddress, self.linePassword)
        dialogPreferences.setTabOrder(self.linePassword, self.lineBuildName)
        dialogPreferences.setTabOrder(self.lineBuildName, self.lineUsername)
        dialogPreferences.setTabOrder(self.lineUsername, self.lineEmailAddress)
        dialogPreferences.setTabOrder(self.lineEmailAddress, self.pushApply)
        dialogPreferences.setTabOrder(self.pushApply, self.pushOK)
        dialogPreferences.setTabOrder(self.pushOK, self.pushCancel)

    def retranslateUi(self, dialogPreferences):
        _translate = QtCore.QCoreApplication.translate
        dialogPreferences.setWindowTitle(_translate("dialogPreferences", "Preferences"))
        self.groupSliceConverter.setTitle(_translate("dialogPreferences", "Slice Converter Settings"))
        self.labelCentrelineT.setText(_translate("dialogPreferences", "Centreline Thickness"))
        self.spinContourT.setToolTip(_translate("dialogPreferences", "1 - 25"))
        self.labelContourT.setText(_translate("dialogPreferences", "Contour Thickness"))
        self.spinCentrelineT.setToolTip(_translate("dialogPreferences", "1 - 25"))
        self.labelROIOffset.setText(_translate("dialogPreferences", "ROI Offset"))
        self.spinROIOffset.setToolTip(_translate("dialogPreferences", "1 - 5000"))
        self.pushApply.setText(_translate("dialogPreferences", "Apply"))
        self.pushOK.setText(_translate("dialogPreferences", "OK"))
        self.pushCancel.setText(_translate("dialogPreferences", "Cancel"))
        self.groupIdleTimeout.setToolTip(_translate("dialogPreferences", "Set to 0 minutes to disable idle notifications."))
        self.groupIdleTimeout.setTitle(_translate("dialogPreferences", "Idle Timeout"))
        self.labelMinutes.setText(_translate("dialogPreferences", "Minutes"))
        self.spinIdleTimeout.setToolTip(_translate("dialogPreferences", "0 - 180"))
        self.groupGridline.setTitle(_translate("dialogPreferences", "Gridline Settings"))
        self.spinThickness.setToolTip(_translate("dialogPreferences", "1 - 10"))
        self.labelSize.setText(_translate("dialogPreferences", "Grid Size (Pixels)"))
        self.labelThickness.setText(_translate("dialogPreferences", "Gridline Thickness"))
        self.spinSize.setToolTip(_translate("dialogPreferences", "5 - 1205"))
        self.groupBuildDefaults.setTitle(_translate("dialogPreferences", "Build Defaults"))
        self.labelBuildName.setText(_translate("dialogPreferences", "Build Name"))
        self.labelUsername.setText(_translate("dialogPreferences", "Username"))
        self.labelEmailAddress.setText(_translate("dialogPreferences", "Email Address"))
        self.groupBox.setTitle(_translate("dialogPreferences", "Notifications"))
        self.labelSenderAddress.setText(_translate("dialogPreferences", "Sender Address"))
        self.labelPassword.setText(_translate("dialogPreferences", "Password"))
        self.label.setText(_translate("dialogPreferences", "Please ensure that the entered email addresses are valid and correct."))
        self.labelBuildFolder.setText(_translate("dialogPreferences", "Build Folder"))
        self.pushBrowseBF.setText(_translate("dialogPreferences", "Browse..."))

