# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogSliceConverter.ui'
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

class Ui_dialogSliceConverter(object):
    def setupUi(self, dialogSliceConverter):
        dialogSliceConverter.setObjectName(_fromUtf8("dialogSliceConverter"))
        dialogSliceConverter.resize(411, 358)
        dialogSliceConverter.setMinimumSize(QtCore.QSize(411, 358))
        dialogSliceConverter.setMaximumSize(QtCore.QSize(411, 358))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSliceConverter.setWindowIcon(icon)
        dialogSliceConverter.setModal(False)
        self.labelInformation = QtGui.QLabel(dialogSliceConverter)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 391, 63))
        self.labelInformation.setScaledContents(False)
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName(_fromUtf8("labelInformation"))
        self.buttonBrowseSF = QtGui.QPushButton(dialogSliceConverter)
        self.buttonBrowseSF.setGeometry(QtCore.QRect(290, 80, 111, 28))
        self.buttonBrowseSF.setObjectName(_fromUtf8("buttonBrowseSF"))
        self.buttonStartConversion = QtGui.QPushButton(dialogSliceConverter)
        self.buttonStartConversion.setEnabled(False)
        self.buttonStartConversion.setGeometry(QtCore.QRect(10, 318, 271, 28))
        self.buttonStartConversion.setObjectName(_fromUtf8("buttonStartConversion"))
        self.buttonDone = QtGui.QPushButton(dialogSliceConverter)
        self.buttonDone.setGeometry(QtCore.QRect(290, 318, 111, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.progressBar = QtGui.QProgressBar(dialogSliceConverter)
        self.progressBar.setGeometry(QtCore.QRect(10, 284, 391, 28))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.labelStatus = QtGui.QLabel(dialogSliceConverter)
        self.labelStatus.setGeometry(QtCore.QRect(10, 250, 391, 28))
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.labelStatusSlice = QtGui.QLabel(dialogSliceConverter)
        self.labelStatusSlice.setGeometry(QtCore.QRect(20, 216, 371, 28))
        self.labelStatusSlice.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelStatusSlice.setObjectName(_fromUtf8("labelStatusSlice"))
        self.checkDraw = QtGui.QCheckBox(dialogSliceConverter)
        self.checkDraw.setEnabled(True)
        self.checkDraw.setGeometry(QtCore.QRect(290, 114, 111, 28))
        self.checkDraw.setObjectName(_fromUtf8("checkDraw"))
        self.listSliceFiles = QtGui.QListWidget(dialogSliceConverter)
        self.listSliceFiles.setGeometry(QtCore.QRect(10, 80, 271, 96))
        self.listSliceFiles.setObjectName(_fromUtf8("listSliceFiles"))
        self.lineFolder = QtGui.QLineEdit(dialogSliceConverter)
        self.lineFolder.setGeometry(QtCore.QRect(10, 183, 271, 26))
        self.lineFolder.setReadOnly(True)
        self.lineFolder.setObjectName(_fromUtf8("lineFolder"))
        self.buttonBrowseF = QtGui.QPushButton(dialogSliceConverter)
        self.buttonBrowseF.setGeometry(QtCore.QRect(290, 182, 111, 28))
        self.buttonBrowseF.setObjectName(_fromUtf8("buttonBrowseF"))

        self.retranslateUi(dialogSliceConverter)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogSliceConverter.close)
        QtCore.QMetaObject.connectSlotsByName(dialogSliceConverter)

    def retranslateUi(self, dialogSliceConverter):
        dialogSliceConverter.setWindowTitle(_translate("dialogSliceConverter", "Slice Converter", None))
        self.labelInformation.setText(_translate("dialogSliceConverter", "Select one or multiple .cls or .cli file(s). The tool will read, parse and convert the data into a list of contours that will be saved as a text file. These contours can then be used to draw all the selected parts onto a blank image, which will be saved to the selected folder.", None))
        self.buttonBrowseSF.setText(_translate("dialogSliceConverter", "Browse...", None))
        self.buttonStartConversion.setText(_translate("dialogSliceConverter", "Start Conversion", None))
        self.buttonDone.setText(_translate("dialogSliceConverter", "Done", None))
        self.labelStatus.setText(_translate("dialogSliceConverter", "Please select a .cls or .cli file(s) to convert.", None))
        self.labelStatusSlice.setText(_translate("dialogSliceConverter", "Current Slice:", None))
        self.checkDraw.setText(_translate("dialogSliceConverter", "Draw Contours", None))
        self.buttonBrowseF.setText(_translate("dialogSliceConverter", "Browse...", None))

import icons_rc
