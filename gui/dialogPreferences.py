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
        dialogPreferences.resize(203, 146)
        self.gridLayout = QtWidgets.QGridLayout(dialogPreferences)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(dialogPreferences)
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
        self.gridLayout_2.addWidget(self.pushModify, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 2)
        self.pushDone = QtWidgets.QPushButton(dialogPreferences)
        self.pushDone.setObjectName("pushDone")
        self.gridLayout.addWidget(self.pushDone, 3, 1, 1, 1)

        self.retranslateUi(dialogPreferences)
        self.pushDone.clicked.connect(dialogPreferences.close)
        QtCore.QMetaObject.connectSlotsByName(dialogPreferences)
        dialogPreferences.setTabOrder(self.spinSize, self.spinThickness)
        dialogPreferences.setTabOrder(self.spinThickness, self.pushModify)
        dialogPreferences.setTabOrder(self.pushModify, self.pushDone)

    def retranslateUi(self, dialogPreferences):
        _translate = QtCore.QCoreApplication.translate
        dialogPreferences.setWindowTitle(_translate("dialogPreferences", "Preferences"))
        self.groupBox.setTitle(_translate("dialogPreferences", "Gridline Settings"))
        self.labelThickness.setText(_translate("dialogPreferences", "Gridline Thickness"))
        self.spinThickness.setToolTip(_translate("dialogPreferences", "1 - 10"))
        self.labelSize.setText(_translate("dialogPreferences", "Grid Size (Pixels)"))
        self.pushModify.setText(_translate("dialogPreferences", "Modify"))
        self.pushDone.setText(_translate("dialogPreferences", "Done"))

