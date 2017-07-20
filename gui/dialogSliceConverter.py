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
        dialogSliceConverter.resize(381, 210)
        dialogSliceConverter.setMinimumSize(QtCore.QSize(381, 210))
        dialogSliceConverter.setMaximumSize(QtCore.QSize(381, 210))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogSliceConverter.setWindowIcon(icon)
        dialogSliceConverter.setModal(True)
        self.labelInformation = QtGui.QLabel(dialogSliceConverter)
        self.labelInformation.setGeometry(QtCore.QRect(10, 10, 361, 51))
        self.labelInformation.setScaledContents(False)
        self.labelInformation.setWordWrap(True)
        self.labelInformation.setObjectName(_fromUtf8("labelInformation"))
        self.buttonBrowse = QtGui.QPushButton(dialogSliceConverter)
        self.buttonBrowse.setGeometry(QtCore.QRect(280, 69, 91, 28))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.buttonStartConversion = QtGui.QPushButton(dialogSliceConverter)
        self.buttonStartConversion.setEnabled(False)
        self.buttonStartConversion.setGeometry(QtCore.QRect(10, 172, 261, 28))
        self.buttonStartConversion.setObjectName(_fromUtf8("buttonStartConversion"))
        self.buttonDone = QtGui.QPushButton(dialogSliceConverter)
        self.buttonDone.setGeometry(QtCore.QRect(280, 172, 91, 28))
        self.buttonDone.setObjectName(_fromUtf8("buttonDone"))
        self.progressBar = QtGui.QProgressBar(dialogSliceConverter)
        self.progressBar.setGeometry(QtCore.QRect(10, 138, 361, 28))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.labelStatus = QtGui.QLabel(dialogSliceConverter)
        self.labelStatus.setGeometry(QtCore.QRect(10, 104, 361, 28))
        self.labelStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.lineSliceFile = QtGui.QLineEdit(dialogSliceConverter)
        self.lineSliceFile.setGeometry(QtCore.QRect(10, 70, 261, 26))
        self.lineSliceFile.setReadOnly(True)
        self.lineSliceFile.setObjectName(_fromUtf8("lineSliceFile"))

        self.retranslateUi(dialogSliceConverter)
        QtCore.QObject.connect(self.buttonDone, QtCore.SIGNAL(_fromUtf8("clicked()")), dialogSliceConverter.accept)
        QtCore.QMetaObject.connectSlotsByName(dialogSliceConverter)

    def retranslateUi(self, dialogSliceConverter):
        dialogSliceConverter.setWindowTitle(_translate("dialogSliceConverter", "Slice Converter", None))
        self.labelInformation.setText(_translate("dialogSliceConverter", "To convert a .cls or .cli file, please select the file in question. The parsed slice will be saved as a text document with the same name in the same folder. ", None))
        self.buttonBrowse.setText(_translate("dialogSliceConverter", "Browse...", None))
        self.buttonStartConversion.setText(_translate("dialogSliceConverter", "Start Conversion", None))
        self.buttonDone.setText(_translate("dialogSliceConverter", "Done", None))
        self.labelStatus.setText(_translate("dialogSliceConverter", "Please select a .cls or .cli file to convert.", None))

import icons_rc
