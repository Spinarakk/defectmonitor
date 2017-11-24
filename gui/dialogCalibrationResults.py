# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogCalibrationResults.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogCalibrationResults(object):
    def setupUi(self, dialogCalibrationResults):
        dialogCalibrationResults.setObjectName("dialogCalibrationResults")
        dialogCalibrationResults.resize(284, 332)
        self.gridLayout = QtWidgets.QGridLayout(dialogCalibrationResults)
        self.gridLayout.setObjectName("gridLayout")
        self.labelCameraMatrix = QtWidgets.QLabel(dialogCalibrationResults)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelCameraMatrix.setFont(font)
        self.labelCameraMatrix.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCameraMatrix.setObjectName("labelCameraMatrix")
        self.gridLayout.addWidget(self.labelCameraMatrix, 0, 0, 1, 2)
        self.labelDistortionCoefficients = QtWidgets.QLabel(dialogCalibrationResults)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelDistortionCoefficients.setFont(font)
        self.labelDistortionCoefficients.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDistortionCoefficients.setObjectName("labelDistortionCoefficients")
        self.gridLayout.addWidget(self.labelDistortionCoefficients, 2, 0, 1, 2)
        self.labelHomographyMatrix = QtWidgets.QLabel(dialogCalibrationResults)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelHomographyMatrix.setFont(font)
        self.labelHomographyMatrix.setAlignment(QtCore.Qt.AlignCenter)
        self.labelHomographyMatrix.setObjectName("labelHomographyMatrix")
        self.gridLayout.addWidget(self.labelHomographyMatrix, 4, 0, 1, 2)
        self.labelRMS = QtWidgets.QLabel(dialogCalibrationResults)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.labelRMS.setFont(font)
        self.labelRMS.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelRMS.setObjectName("labelRMS")
        self.gridLayout.addWidget(self.labelRMS, 6, 0, 1, 1)
        self.pushDone = QtWidgets.QPushButton(dialogCalibrationResults)
        self.pushDone.setObjectName("pushDone")
        self.gridLayout.addWidget(self.pushDone, 6, 1, 1, 1)
        self.tableCM = QtWidgets.QTableWidget(dialogCalibrationResults)
        self.tableCM.setEnabled(True)
        self.tableCM.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableCM.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableCM.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableCM.setRowCount(3)
        self.tableCM.setColumnCount(3)
        self.tableCM.setObjectName("tableCM")
        self.tableCM.horizontalHeader().setVisible(False)
        self.tableCM.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableCM, 1, 0, 1, 2)
        self.tableHM = QtWidgets.QTableWidget(dialogCalibrationResults)
        self.tableHM.setEnabled(True)
        self.tableHM.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableHM.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableHM.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableHM.setRowCount(3)
        self.tableHM.setColumnCount(3)
        self.tableHM.setObjectName("tableHM")
        self.tableHM.horizontalHeader().setVisible(False)
        self.tableHM.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableHM, 5, 0, 1, 2)
        self.tableDC = QtWidgets.QTableWidget(dialogCalibrationResults)
        self.tableDC.setEnabled(True)
        self.tableDC.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableDC.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableDC.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableDC.setRowCount(2)
        self.tableDC.setColumnCount(3)
        self.tableDC.setObjectName("tableDC")
        self.tableDC.horizontalHeader().setVisible(False)
        self.tableDC.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableDC, 3, 0, 1, 2)

        self.retranslateUi(dialogCalibrationResults)
        self.pushDone.clicked.connect(dialogCalibrationResults.close)
        QtCore.QMetaObject.connectSlotsByName(dialogCalibrationResults)

    def retranslateUi(self, dialogCalibrationResults):
        _translate = QtCore.QCoreApplication.translate
        dialogCalibrationResults.setWindowTitle(_translate("dialogCalibrationResults", "Calibration Results"))
        self.labelCameraMatrix.setToolTip(_translate("dialogCalibrationResults", "Matrix that describes the mapping of a pinhole camera from 3D points in the real world to 2D points in an image."))
        self.labelCameraMatrix.setText(_translate("dialogCalibrationResults", "Camera Matrix"))
        self.labelDistortionCoefficients.setToolTip(_translate("dialogCalibrationResults", "Values that specify how to undistort the image to correct any radial and tangential distortion caused by pinhole cameras."))
        self.labelDistortionCoefficients.setText(_translate("dialogCalibrationResults", "Distortion Coefficients"))
        self.labelHomographyMatrix.setToolTip(_translate("dialogCalibrationResults", "Matrix that describes the relation of two images with the same planar surface in space that is used to warp the perspective of an image onto another."))
        self.labelHomographyMatrix.setText(_translate("dialogCalibrationResults", "Homography Matrix"))
        self.labelRMS.setToolTip(_translate("dialogCalibrationResults", "Geometric error corresponding to the image distance between a projected point and a measured one. An acceptable error should be less than 1 pixel."))
        self.labelRMS.setText(_translate("dialogCalibrationResults", "Re-Projection Error: 0.000000000"))
        self.pushDone.setText(_translate("dialogCalibrationResults", "Done"))

