# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui\dialogSliceConverter.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dialogSliceConverter(object):
    def setupUi(self, dialogSliceConverter):
        dialogSliceConverter.setObjectName("dialogSliceConverter")
        dialogSliceConverter.resize(411, 358)
        dialogSliceConverter.setMinimumSize(QtCore.QSize(411, 358))
        dialogSliceConverter.setMaximumSize(QtCore.QSize(411, 358))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSliceConverter.setWindowIcon(icon)
        self.labelInformation = QtWidgets.QLabel(dialogSliceConverter)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 391, 63))
        self.labelInformation.setScaledContents(False)
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName("labelInformation")
        self.buttonBrowseSF = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonBrowseSF.setGeometry(QtCore.QRect(290, 80, 111, 28))
        self.buttonBrowseSF.setObjectName("buttonBrowseSF")
        self.buttonStart = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonStart.setEnabled(False)
        self.buttonStart.setGeometry(QtCore.QRect(10, 318, 271, 28))
        self.buttonStart.setObjectName("buttonStart")
        self.buttonDone = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonDone.setGeometry(QtCore.QRect(290, 318, 111, 28))
        self.buttonDone.setObjectName("buttonDone")
        self.progressBar = QtWidgets.QProgressBar(dialogSliceConverter)
        self.progressBar.setGeometry(QtCore.QRect(10, 284, 391, 28))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.labelStatus = QtWidgets.QLabel(dialogSliceConverter)
        self.labelStatus.setGeometry(QtCore.QRect(10, 250, 391, 28))
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatusSlice = QtWidgets.QLabel(dialogSliceConverter)
        self.labelStatusSlice.setGeometry(QtCore.QRect(10, 216, 391, 28))
        self.labelStatusSlice.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatusSlice.setObjectName("labelStatusSlice")
        self.checkDraw = QtWidgets.QCheckBox(dialogSliceConverter)
        self.checkDraw.setEnabled(True)
        self.checkDraw.setGeometry(QtCore.QRect(290, 114, 111, 28))
        self.checkDraw.setObjectName("checkDraw")
        self.listSliceFiles = QtWidgets.QListWidget(dialogSliceConverter)
        self.listSliceFiles.setGeometry(QtCore.QRect(10, 80, 271, 96))
        self.listSliceFiles.setObjectName("listSliceFiles")
        self.lineFolder = QtWidgets.QLineEdit(dialogSliceConverter)
        self.lineFolder.setGeometry(QtCore.QRect(10, 183, 271, 26))
        self.lineFolder.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineFolder.setReadOnly(True)
        self.lineFolder.setObjectName("lineFolder")
        self.buttonBrowseF = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonBrowseF.setGeometry(QtCore.QRect(290, 182, 111, 28))
        self.buttonBrowseF.setObjectName("buttonBrowseF")

        self.retranslateUi(dialogSliceConverter)
        self.buttonDone.clicked.connect(dialogSliceConverter.close)
        QtCore.QMetaObject.connectSlotsByName(dialogSliceConverter)
        dialogSliceConverter.setTabOrder(self.listSliceFiles, self.buttonBrowseSF)
        dialogSliceConverter.setTabOrder(self.buttonBrowseSF, self.checkDraw)
        dialogSliceConverter.setTabOrder(self.checkDraw, self.buttonBrowseF)
        dialogSliceConverter.setTabOrder(self.buttonBrowseF, self.buttonStart)
        dialogSliceConverter.setTabOrder(self.buttonStart, self.buttonDone)

    def retranslateUi(self, dialogSliceConverter):
        _translate = QtCore.QCoreApplication.translate
        dialogSliceConverter.setWindowTitle(_translate("dialogSliceConverter", "Slice Converter"))
        self.labelInformation.setText(_translate("dialogSliceConverter", "Select one or multiple .cls or .cli file(s). The tool will read, parse and convert the data into a list of contours that will be saved as a text file. These contours can then be used to draw all the selected parts onto a blank image, which will be saved to the selected folder."))
        self.buttonBrowseSF.setText(_translate("dialogSliceConverter", "Browse..."))
        self.buttonStart.setText(_translate("dialogSliceConverter", "Start"))
        self.buttonDone.setText(_translate("dialogSliceConverter", "Done"))
        self.labelStatus.setText(_translate("dialogSliceConverter", "Please select a .cls or .cli file(s) to convert."))
        self.labelStatusSlice.setText(_translate("dialogSliceConverter", "Current Part: None"))
        self.checkDraw.setText(_translate("dialogSliceConverter", "Draw Contours"))
        self.buttonBrowseF.setText(_translate("dialogSliceConverter", "Browse..."))

