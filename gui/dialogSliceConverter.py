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
        dialogSliceConverter.resize(415, 288)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSliceConverter.setWindowIcon(icon)
        dialogSliceConverter.setModal(True)
        self.labelInformation = QtGui.QLabel(dialogSliceConverter)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 391, 61))
        self.labelInformation.setScaledContents(False)
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName(_fromUtf8("labelInformation"))
        self.buttonBrowse = QtGui.QPushButton(dialogSliceConverter)
        self.buttonBrowse.setGeometry(QtCore.QRect(310, 80, 91, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.buttonStartConversion = QtGui.QPushButton(dialogSliceConverter)
        self.buttonStartConversion.setEnabled(False)
        self.buttonStartConversion.setGeometry(QtCore.QRect(10, 250, 291, 28))
        self.buttonStartConversion.setObjectName(_fromUtf8("buttonStartConversion"))
        self.buttonDone = QtGui.QPushButton(dialogSliceConverter)
        self.buttonDone.setGeometry(QtCore.QRect(310, 250, 91, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.progressBar = QtGui.QProgressBar(dialogSliceConverter)
        self.progressBar.setGeometry(QtCore.QRect(10, 216, 391, 28))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.labelStatus = QtGui.QLabel(dialogSliceConverter)
        self.labelStatus.setGeometry(QtCore.QRect(10, 182, 391, 28))
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.lineSliceFile = QtGui.QLineEdit(dialogSliceConverter)
        self.lineSliceFile.setGeometry(QtCore.QRect(10, 80, 291, 26))
        self.lineSliceFile.setReadOnly(True)
        self.lineSliceFile.setObjectName(_fromUtf8("lineSliceFile"))
        self.checkContours = QtGui.QCheckBox(dialogSliceConverter)
        self.checkContours.setGeometry(QtCore.QRect(10, 114, 111, 28))
        self.checkContours.setObjectName(_fromUtf8("checkContours"))
        self.checkFill = QtGui.QCheckBox(dialogSliceConverter)
        self.checkFill.setEnabled(False)
        self.checkFill.setGeometry(QtCore.QRect(150, 114, 101, 28))
        self.checkFill.setObjectName(_fromUtf8("checkFill"))
        self.checkSave = QtGui.QCheckBox(dialogSliceConverter)
        self.checkSave.setEnabled(False)
        self.checkSave.setGeometry(QtCore.QRect(270, 114, 131, 28))
        self.checkSave.setObjectName(_fromUtf8("checkSave"))
        self.labelStatusSlice = QtGui.QLabel(dialogSliceConverter)
        self.labelStatusSlice.setGeometry(QtCore.QRect(10, 148, 251, 28))
        self.labelStatusSlice.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelStatusSlice.setObjectName(_fromUtf8("labelStatusSlice"))
        self.checkCombine = QtGui.QCheckBox(dialogSliceConverter)
        self.checkCombine.setEnabled(True)
        self.checkCombine.setGeometry(QtCore.QRect(270, 150, 131, 28))
        self.checkCombine.setObjectName(_fromUtf8("checkCombine"))

        self.retranslateUi(dialogSliceConverter)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogSliceConverter.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogSliceConverter)

    def retranslateUi(self, dialogSliceConverter):
        dialogSliceConverter.setWindowTitle(_translate("dialogSliceConverter", "Slice Converter", None))
        self.labelInformation.setText(_translate("dialogSliceConverter", "To convert a .cls or .cli file, please select the file in question. If multiple files are selected, each file will be converted and an option to combine all the drawn contours will be enabled. The contour data will be saved as a JSON file with the same name in the same folder. ", None))
        self.buttonBrowse.setText(_translate("dialogSliceConverter", "Browse...", None))
        self.buttonStartConversion.setText(_translate("dialogSliceConverter", "Start Conversion", None))
        self.buttonDone.setText(_translate("dialogSliceConverter", "Done", None))
        self.labelStatus.setText(_translate("dialogSliceConverter", "Please select a .cls or .cli file(s) to convert.", None))
        self.checkContours.setText(_translate("dialogSliceConverter", "Draw Contours", None))
        self.checkFill.setText(_translate("dialogSliceConverter", "Fill Contours", None))
        self.checkSave.setText(_translate("dialogSliceConverter", "Save Contours", None))
        self.labelStatusSlice.setText(_translate("dialogSliceConverter", "Current Slice:", None))
        self.checkCombine.setText(_translate("dialogSliceConverter", "Combine Contours", None))

import icons_rc
