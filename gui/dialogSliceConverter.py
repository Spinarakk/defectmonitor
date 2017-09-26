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
        dialogSliceConverter.resize(275, 214)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSliceConverter.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(dialogSliceConverter)
        self.gridLayout.setObjectName("gridLayout")
        self.labelStatus = QtWidgets.QLabel(dialogSliceConverter)
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName("labelStatus")
        self.gridLayout.addWidget(self.labelStatus, 7, 0, 1, 3)
        self.buttonStart = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonStart.setEnabled(False)
        self.buttonStart.setObjectName("buttonStart")
        self.gridLayout.addWidget(self.buttonStart, 9, 0, 1, 1)
        self.buttonStop = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonStop.setEnabled(False)
        self.buttonStop.setObjectName("buttonStop")
        self.gridLayout.addWidget(self.buttonStop, 9, 1, 1, 1)
        self.buttonBrowseSF = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonBrowseSF.setObjectName("buttonBrowseSF")
        self.gridLayout.addWidget(self.buttonBrowseSF, 0, 2, 1, 1)
        self.buttonBrowseF = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonBrowseF.setObjectName("buttonBrowseF")
        self.gridLayout.addWidget(self.buttonBrowseF, 5, 2, 1, 1)
        self.buttonDone = QtWidgets.QPushButton(dialogSliceConverter)
        self.buttonDone.setObjectName("buttonDone")
        self.gridLayout.addWidget(self.buttonDone, 9, 2, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(dialogSliceConverter)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 8, 0, 1, 3)
        self.listSliceFiles = QtWidgets.QListWidget(dialogSliceConverter)
        self.listSliceFiles.setObjectName("listSliceFiles")
        self.gridLayout.addWidget(self.listSliceFiles, 0, 0, 4, 2)
        self.lineFolder = QtWidgets.QLineEdit(dialogSliceConverter)
        self.lineFolder.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lineFolder.setReadOnly(True)
        self.lineFolder.setObjectName("lineFolder")
        self.gridLayout.addWidget(self.lineFolder, 5, 0, 1, 2)
        self.labelStatusSlice = QtWidgets.QLabel(dialogSliceConverter)
        self.labelStatusSlice.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatusSlice.setObjectName("labelStatusSlice")
        self.gridLayout.addWidget(self.labelStatusSlice, 6, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 2, 1, 1)
        self.checkDraw = QtWidgets.QCheckBox(dialogSliceConverter)
        self.checkDraw.setEnabled(True)
        self.checkDraw.setObjectName("checkDraw")
        self.gridLayout.addWidget(self.checkDraw, 1, 2, 1, 1)

        self.retranslateUi(dialogSliceConverter)
        self.buttonDone.clicked.connect(dialogSliceConverter.close)
        QtCore.QMetaObject.connectSlotsByName(dialogSliceConverter)
        dialogSliceConverter.setTabOrder(self.listSliceFiles, self.buttonBrowseSF)
        dialogSliceConverter.setTabOrder(self.buttonBrowseSF, self.buttonBrowseF)
        dialogSliceConverter.setTabOrder(self.buttonBrowseF, self.buttonStart)
        dialogSliceConverter.setTabOrder(self.buttonStart, self.buttonDone)

    def retranslateUi(self, dialogSliceConverter):
        _translate = QtCore.QCoreApplication.translate
        dialogSliceConverter.setWindowTitle(_translate("dialogSliceConverter", "Slice Converter"))
        self.labelStatus.setText(_translate("dialogSliceConverter", "Please select a .cls or .cli file(s) to convert."))
        self.buttonStart.setText(_translate("dialogSliceConverter", "Start"))
        self.buttonStop.setText(_translate("dialogSliceConverter", "Stop"))
        self.buttonBrowseSF.setText(_translate("dialogSliceConverter", "Browse..."))
        self.buttonBrowseF.setText(_translate("dialogSliceConverter", "Browse..."))
        self.buttonDone.setText(_translate("dialogSliceConverter", "Done"))
        self.labelStatusSlice.setText(_translate("dialogSliceConverter", "Current Part: None"))
        self.checkDraw.setText(_translate("dialogSliceConverter", "Draw Contours"))

