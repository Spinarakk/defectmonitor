# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialogNewBuild.ui'
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

class Ui_dialogNewBuild(object):
    def setupUi(self, dialogNewBuild):
        dialogNewBuild.setObjectName(_fromUtf8("dialogNewBuild"))
        dialogNewBuild.setWindowModality(QtCore.Qt.NonModal)
        dialogNewBuild.resize(430, 218)
        dialogNewBuild.setMinimumSize(QtCore.QSize(430, 218))
        dialogNewBuild.setMaximumSize(QtCore.QSize(430, 218))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dialogNewBuild.setWindowIcon(icon)
        dialogNewBuild.setModal(True)
        self.lineBuildName = QtGui.QLineEdit(dialogNewBuild)
        self.lineBuildName.setGeometry(QtCore.QRect(140, 10, 281, 26))
        self.lineBuildName.setMaxLength(30)
        self.lineBuildName.setObjectName(_fromUtf8("lineBuildName"))
        self.comboPlatform = QtGui.QComboBox(dialogNewBuild)
        self.comboPlatform.setGeometry(QtCore.QRect(140, 44, 281, 26))
        self.comboPlatform.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.comboPlatform.setObjectName(_fromUtf8("comboPlatform"))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.comboPlatform.addItem(_fromUtf8(""))
        self.labelBuildPlatform = QtGui.QLabel(dialogNewBuild)
        self.labelBuildPlatform.setGeometry(QtCore.QRect(10, 44, 121, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelBuildPlatform.setFont(font)
        self.labelBuildPlatform.setObjectName(_fromUtf8("labelBuildPlatform"))
        self.buttonChangeBF = QtGui.QPushButton(dialogNewBuild)
        self.buttonChangeBF.setGeometry(QtCore.QRect(10, 180, 211, 28))
        self.buttonChangeBF.setObjectName(_fromUtf8("buttonChangeBF"))
        self.labelBuildName = QtGui.QLabel(dialogNewBuild)
        self.labelBuildName.setGeometry(QtCore.QRect(10, 10, 101, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelBuildName.setFont(font)
        self.labelBuildName.setObjectName(_fromUtf8("labelBuildName"))
        self.buttonBox = QtGui.QDialogButtonBox(dialogNewBuild)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(230, 180, 191, 28))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.labelCalibrationFile = QtGui.QLabel(dialogNewBuild)
        self.labelCalibrationFile.setGeometry(QtCore.QRect(10, 78, 121, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelCalibrationFile.setFont(font)
        self.labelCalibrationFile.setObjectName(_fromUtf8("labelCalibrationFile"))
        self.labelSliceFile = QtGui.QLabel(dialogNewBuild)
        self.labelSliceFile.setGeometry(QtCore.QRect(10, 112, 121, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.labelSliceFile.setFont(font)
        self.labelSliceFile.setObjectName(_fromUtf8("labelSliceFile"))
        self.lineCalibrationFile = QtGui.QLineEdit(dialogNewBuild)
        self.lineCalibrationFile.setGeometry(QtCore.QRect(140, 78, 181, 26))
        self.lineCalibrationFile.setReadOnly(True)
        self.lineCalibrationFile.setObjectName(_fromUtf8("lineCalibrationFile"))
        self.lineSliceFile = QtGui.QLineEdit(dialogNewBuild)
        self.lineSliceFile.setGeometry(QtCore.QRect(140, 112, 181, 26))
        self.lineSliceFile.setReadOnly(True)
        self.lineSliceFile.setObjectName(_fromUtf8("lineSliceFile"))
        self.buttonBrowseCF = QtGui.QPushButton(dialogNewBuild)
        self.buttonBrowseCF.setGeometry(QtCore.QRect(330, 77, 91, 28))
        self.buttonBrowseCF.setToolTip(_fromUtf8(""))
        self.buttonBrowseCF.setStatusTip(_fromUtf8(""))
        self.buttonBrowseCF.setObjectName(_fromUtf8("buttonBrowseCF"))
        self.buttonBrowseSF = QtGui.QPushButton(dialogNewBuild)
        self.buttonBrowseSF.setGeometry(QtCore.QRect(330, 111, 91, 28))
        self.buttonBrowseSF.setToolTip(_fromUtf8(""))
        self.buttonBrowseSF.setStatusTip(_fromUtf8(""))
        self.buttonBrowseSF.setObjectName(_fromUtf8("buttonBrowseSF"))
        self.lineBuildFolder = QtGui.QLineEdit(dialogNewBuild)
        self.lineBuildFolder.setGeometry(QtCore.QRect(10, 146, 411, 26))
        self.lineBuildFolder.setReadOnly(True)
        self.lineBuildFolder.setObjectName(_fromUtf8("lineBuildFolder"))

        self.retranslateUi(dialogNewBuild)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dialogNewBuild.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dialogNewBuild.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogNewBuild)

    def retranslateUi(self, dialogNewBuild):
        dialogNewBuild.setWindowTitle(_translate("dialogNewBuild", "New Build", None))
        self.lineBuildName.setText(_translate("dialogNewBuild", "Default", None))
        self.comboPlatform.setItemText(0, _translate("dialogNewBuild", "Concept X1000R (636 x 406 mm)", None))
        self.comboPlatform.setItemText(1, _translate("dialogNewBuild", "Concept X2000R (800 x 400 mm)", None))
        self.comboPlatform.setItemText(2, _translate("dialogNewBuild", "EOS M280/M290 (250 x 250 mm)", None))
        self.labelBuildPlatform.setText(_translate("dialogNewBuild", "Build Platform", None))
        self.buttonChangeBF.setToolTip(_translate("dialogNewBuild", "Change where the captured images for the current build will be stored.", None))
        self.buttonChangeBF.setText(_translate("dialogNewBuild", "Change Build Folder", None))
        self.labelBuildName.setText(_translate("dialogNewBuild", "Build Name", None))
        self.labelCalibrationFile.setText(_translate("dialogNewBuild", "Calibration File", None))
        self.labelSliceFile.setText(_translate("dialogNewBuild", "Slice File", None))
        self.buttonBrowseCF.setText(_translate("dialogNewBuild", "Browse", None))
        self.buttonBrowseSF.setText(_translate("dialogNewBuild", "Browse", None))

import icons_rc
