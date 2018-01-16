# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogStressTest.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogStressTest(object):
    def setupUi(self, dialogStressTest):
        dialogStressTest.setObjectName("dialogStressTest")
        dialogStressTest.resize(167, 153)
        self.gridLayout = QtWidgets.QGridLayout(dialogStressTest)
        self.gridLayout.setObjectName("gridLayout")
        self.labelNumber = QtWidgets.QLabel(dialogStressTest)
        self.labelNumber.setAlignment(QtCore.Qt.AlignCenter)
        self.labelNumber.setObjectName("labelNumber")
        self.gridLayout.addWidget(self.labelNumber, 3, 1, 1, 1)
        self.labelImage = QtWidgets.QLabel(dialogStressTest)
        self.labelImage.setObjectName("labelImage")
        self.gridLayout.addWidget(self.labelImage, 3, 0, 1, 1)
        self.labelElapsedTime = QtWidgets.QLabel(dialogStressTest)
        self.labelElapsedTime.setAlignment(QtCore.Qt.AlignCenter)
        self.labelElapsedTime.setObjectName("labelElapsedTime")
        self.gridLayout.addWidget(self.labelElapsedTime, 2, 1, 1, 1)
        self.pushDone = QtWidgets.QPushButton(dialogStressTest)
        self.pushDone.setObjectName("pushDone")
        self.gridLayout.addWidget(self.pushDone, 5, 0, 1, 2)
        self.pushStart = QtWidgets.QPushButton(dialogStressTest)
        self.pushStart.setObjectName("pushStart")
        self.gridLayout.addWidget(self.pushStart, 0, 0, 1, 2)
        self.spinInterval = QtWidgets.QSpinBox(dialogStressTest)
        self.spinInterval.setMinimum(1)
        self.spinInterval.setProperty("value", 10)
        self.spinInterval.setObjectName("spinInterval")
        self.gridLayout.addWidget(self.spinInterval, 1, 1, 1, 1)
        self.labelInterval = QtWidgets.QLabel(dialogStressTest)
        self.labelInterval.setObjectName("labelInterval")
        self.gridLayout.addWidget(self.labelInterval, 1, 0, 1, 1)
        self.labelElapsed = QtWidgets.QLabel(dialogStressTest)
        self.labelElapsed.setObjectName("labelElapsed")
        self.gridLayout.addWidget(self.labelElapsed, 2, 0, 1, 1)
        self.labelStatus = QtWidgets.QLabel(dialogStressTest)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout.addWidget(self.labelStatus, 4, 0, 1, 2)

        self.retranslateUi(dialogStressTest)
        self.pushDone.clicked.connect(dialogStressTest.close)
        QtCore.QMetaObject.connectSlotsByName(dialogStressTest)

    def retranslateUi(self, dialogStressTest):
        _translate = QtCore.QCoreApplication.translate
        dialogStressTest.setWindowTitle(_translate("dialogStressTest", "Stress Test"))
        self.labelNumber.setText(_translate("dialogStressTest", "0000"))
        self.labelImage.setText(_translate("dialogStressTest", "Number of Images"))
        self.labelElapsedTime.setText(_translate("dialogStressTest", "00:00:00"))
        self.pushDone.setText(_translate("dialogStressTest", "Done"))
        self.pushStart.setText(_translate("dialogStressTest", "Start"))
        self.labelInterval.setText(_translate("dialogStressTest", "Capture Interval (s)"))
        self.labelElapsed.setText(_translate("dialogStressTest", "Elapsed Time"))
        self.labelStatus.setText(_translate("dialogStressTest", "Waiting"))

