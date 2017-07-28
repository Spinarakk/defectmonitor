# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
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

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName(_fromUtf8("mainWindow"))
        mainWindow.setEnabled(True)
        mainWindow.resize(1209, 799)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        mainWindow.setMinimumSize(QtCore.QSize(1209, 799))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/resources/logo.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        mainWindow.setWindowIcon(icon)
        mainWindow.setStatusTip(_fromUtf8(""))
        mainWindow.setIconSize(QtCore.QSize(24, 24))
        mainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.mainWidget = QtGui.QWidget(mainWindow)
        self.mainWidget.setObjectName(_fromUtf8("mainWidget"))
        self.gridLayout_4 = QtGui.QGridLayout(self.mainWidget)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.groupPositionAdjustment = QtGui.QGroupBox(self.mainWidget)
        self.groupPositionAdjustment.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupPositionAdjustment.sizePolicy().hasHeightForWidth())
        self.groupPositionAdjustment.setSizePolicy(sizePolicy)
        self.groupPositionAdjustment.setMinimumSize(QtCore.QSize(131, 201))
        self.groupPositionAdjustment.setMaximumSize(QtCore.QSize(131, 201))
        self.groupPositionAdjustment.setObjectName(_fromUtf8("groupPositionAdjustment"))
        self.buttonCrop = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonCrop.setGeometry(QtCore.QRect(10, 80, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonCrop.setFont(font)
        self.buttonCrop.setCheckable(True)
        self.buttonCrop.setObjectName(_fromUtf8("buttonCrop"))
        self.buttonShiftLeft = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonShiftLeft.setGeometry(QtCore.QRect(10, 120, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonShiftLeft.setFont(font)
        self.buttonShiftLeft.setObjectName(_fromUtf8("buttonShiftLeft"))
        self.buttonShiftRight = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonShiftRight.setGeometry(QtCore.QRect(90, 120, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonShiftRight.setFont(font)
        self.buttonShiftRight.setObjectName(_fromUtf8("buttonShiftRight"))
        self.buttonShiftDown = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonShiftDown.setGeometry(QtCore.QRect(50, 160, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonShiftDown.setFont(font)
        self.buttonShiftDown.setObjectName(_fromUtf8("buttonShiftDown"))
        self.buttonShiftUp = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonShiftUp.setGeometry(QtCore.QRect(50, 80, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonShiftUp.setFont(font)
        self.buttonShiftUp.setObjectName(_fromUtf8("buttonShiftUp"))
        self.buttonRotateACW = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonRotateACW.setGeometry(QtCore.QRect(10, 160, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonRotateACW.setFont(font)
        self.buttonRotateACW.setObjectName(_fromUtf8("buttonRotateACW"))
        self.buttonRotateCW = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonRotateCW.setGeometry(QtCore.QRect(90, 160, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonRotateCW.setFont(font)
        self.buttonRotateCW.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.buttonRotateCW.setObjectName(_fromUtf8("buttonRotateCW"))
        self.labelPixels = QtGui.QLabel(self.groupPositionAdjustment)
        self.labelPixels.setGeometry(QtCore.QRect(70, 25, 50, 20))
        self.labelPixels.setObjectName(_fromUtf8("labelPixels"))
        self.buttonBoundary = QtGui.QPushButton(self.groupPositionAdjustment)
        self.buttonBoundary.setGeometry(QtCore.QRect(90, 80, 31, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonBoundary.setFont(font)
        self.buttonBoundary.setCheckable(True)
        self.buttonBoundary.setObjectName(_fromUtf8("buttonBoundary"))
        self.lineShiftDegrees = QtGui.QLineEdit(self.groupPositionAdjustment)
        self.lineShiftDegrees.setGeometry(QtCore.QRect(20, 50, 41, 20))
        self.lineShiftDegrees.setMaxLength(5)
        self.lineShiftDegrees.setEchoMode(QtGui.QLineEdit.Normal)
        self.lineShiftDegrees.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineShiftDegrees.setObjectName(_fromUtf8("lineShiftDegrees"))
        self.lineShiftPixels = QtGui.QLineEdit(self.groupPositionAdjustment)
        self.lineShiftPixels.setGeometry(QtCore.QRect(20, 25, 41, 20))
        self.lineShiftPixels.setMaxLength(2)
        self.lineShiftPixels.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineShiftPixels.setObjectName(_fromUtf8("lineShiftPixels"))
        self.labelDegrees = QtGui.QLabel(self.groupPositionAdjustment)
        self.labelDegrees.setGeometry(QtCore.QRect(70, 50, 50, 20))
        self.labelDegrees.setObjectName(_fromUtf8("labelDegrees"))
        self.gridLayout_4.addWidget(self.groupPositionAdjustment, 5, 3, 1, 1)
        self.groupOpenCV = QtGui.QGroupBox(self.mainWidget)
        self.groupOpenCV.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupOpenCV.sizePolicy().hasHeightForWidth())
        self.groupOpenCV.setSizePolicy(sizePolicy)
        self.groupOpenCV.setMinimumSize(QtCore.QSize(131, 151))
        self.groupOpenCV.setMaximumSize(QtCore.QSize(131, 151))
        self.groupOpenCV.setCheckable(False)
        self.groupOpenCV.setObjectName(_fromUtf8("groupOpenCV"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupOpenCV)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.radioOpenCV1 = QtGui.QRadioButton(self.groupOpenCV)
        self.radioOpenCV1.setChecked(True)
        self.radioOpenCV1.setObjectName(_fromUtf8("radioOpenCV1"))
        self.verticalLayout_2.addWidget(self.radioOpenCV1)
        self.radioOpenCV2 = QtGui.QRadioButton(self.groupOpenCV)
        self.radioOpenCV2.setObjectName(_fromUtf8("radioOpenCV2"))
        self.verticalLayout_2.addWidget(self.radioOpenCV2)
        self.radioOpenCV3 = QtGui.QRadioButton(self.groupOpenCV)
        self.radioOpenCV3.setObjectName(_fromUtf8("radioOpenCV3"))
        self.verticalLayout_2.addWidget(self.radioOpenCV3)
        self.radioOpenCV4 = QtGui.QRadioButton(self.groupOpenCV)
        self.radioOpenCV4.setObjectName(_fromUtf8("radioOpenCV4"))
        self.verticalLayout_2.addWidget(self.radioOpenCV4)
        self.radioOpenCV5 = QtGui.QRadioButton(self.groupOpenCV)
        self.radioOpenCV5.setObjectName(_fromUtf8("radioOpenCV5"))
        self.verticalLayout_2.addWidget(self.radioOpenCV5)
        self.gridLayout_4.addWidget(self.groupOpenCV, 1, 3, 1, 1)
        self.groupDisplayOptions = QtGui.QGroupBox(self.mainWidget)
        self.groupDisplayOptions.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupDisplayOptions.sizePolicy().hasHeightForWidth())
        self.groupDisplayOptions.setSizePolicy(sizePolicy)
        self.groupDisplayOptions.setMinimumSize(QtCore.QSize(131, 161))
        self.groupDisplayOptions.setMaximumSize(QtCore.QSize(131, 161))
        self.groupDisplayOptions.setObjectName(_fromUtf8("groupDisplayOptions"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupDisplayOptions)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.radioRaw = QtGui.QRadioButton(self.groupDisplayOptions)
        self.radioRaw.setObjectName(_fromUtf8("radioRaw"))
        self.verticalLayout.addWidget(self.radioRaw)
        self.radioCorrection = QtGui.QRadioButton(self.groupDisplayOptions)
        self.radioCorrection.setObjectName(_fromUtf8("radioCorrection"))
        self.verticalLayout.addWidget(self.radioCorrection)
        self.radioCrop = QtGui.QRadioButton(self.groupDisplayOptions)
        self.radioCrop.setObjectName(_fromUtf8("radioCrop"))
        self.verticalLayout.addWidget(self.radioCrop)
        self.radioCLAHE = QtGui.QRadioButton(self.groupDisplayOptions)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.radioCLAHE.setFont(font)
        self.radioCLAHE.setChecked(True)
        self.radioCLAHE.setObjectName(_fromUtf8("radioCLAHE"))
        self.verticalLayout.addWidget(self.radioCLAHE)
        self.checkToggleOverlay = QtGui.QCheckBox(self.groupDisplayOptions)
        self.checkToggleOverlay.setObjectName(_fromUtf8("checkToggleOverlay"))
        self.verticalLayout.addWidget(self.checkToggleOverlay)
        self.gridLayout_4.addWidget(self.groupDisplayOptions, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 6, 1, 1, 1)
        self.gridLayout_6 = QtGui.QGridLayout()
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.buttonImageConverter = QtGui.QPushButton(self.mainWidget)
        self.buttonImageConverter.setObjectName(_fromUtf8("buttonImageConverter"))
        self.gridLayout_6.addWidget(self.buttonImageConverter, 1, 1, 1, 1)
        self.buttonDefectProcessing = QtGui.QPushButton(self.mainWidget)
        self.buttonDefectProcessing.setEnabled(False)
        self.buttonDefectProcessing.setObjectName(_fromUtf8("buttonDefectProcessing"))
        self.gridLayout_6.addWidget(self.buttonDefectProcessing, 0, 2, 1, 1)
        self.buttonImageCapture = QtGui.QPushButton(self.mainWidget)
        self.buttonImageCapture.setObjectName(_fromUtf8("buttonImageCapture"))
        self.gridLayout_6.addWidget(self.buttonImageCapture, 1, 2, 1, 1)
        self.buttonNotificationSettings = QtGui.QPushButton(self.mainWidget)
        self.buttonNotificationSettings.setObjectName(_fromUtf8("buttonNotificationSettings"))
        self.gridLayout_6.addWidget(self.buttonNotificationSettings, 0, 1, 1, 1)
        self.buttonDisplayImages = QtGui.QPushButton(self.mainWidget)
        self.buttonDisplayImages.setObjectName(_fromUtf8("buttonDisplayImages"))
        self.gridLayout_6.addWidget(self.buttonDisplayImages, 1, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_6, 6, 2, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout1 = QtGui.QVBoxLayout()
        self.verticalLayout1.setObjectName(_fromUtf8("verticalLayout1"))
        self.labelLayerNumberTitle = QtGui.QLabel(self.mainWidget)
        self.labelLayerNumberTitle.setMinimumSize(QtCore.QSize(93, 26))
        self.labelLayerNumberTitle.setMaximumSize(QtCore.QSize(93, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.labelLayerNumberTitle.setFont(font)
        self.labelLayerNumberTitle.setObjectName(_fromUtf8("labelLayerNumberTitle"))
        self.verticalLayout1.addWidget(self.labelLayerNumberTitle)
        self.labelLayerNumber = QtGui.QLabel(self.mainWidget)
        self.labelLayerNumber.setMinimumSize(QtCore.QSize(93, 26))
        self.labelLayerNumber.setMaximumSize(QtCore.QSize(93, 26))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.labelLayerNumber.setFont(font)
        self.labelLayerNumber.setTextFormat(QtCore.Qt.AutoText)
        self.labelLayerNumber.setAlignment(QtCore.Qt.AlignCenter)
        self.labelLayerNumber.setObjectName(_fromUtf8("labelLayerNumber"))
        self.verticalLayout1.addWidget(self.labelLayerNumber)
        self.gridLayout_3.addLayout(self.verticalLayout1, 0, 1, 2, 1)
        self.progressBar = QtGui.QProgressBar(self.mainWidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setMinimumSize(QtCore.QSize(395, 24))
        self.progressBar.setMaximumSize(QtCore.QSize(395, 24))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout_3.addWidget(self.progressBar, 1, 0, 1, 1)
        self.gridLayout2 = QtGui.QGridLayout()
        self.gridLayout2.setObjectName(_fromUtf8("gridLayout2"))
        self.buttonSet = QtGui.QPushButton(self.mainWidget)
        self.buttonSet.setEnabled(True)
        self.buttonSet.setMinimumSize(QtCore.QSize(46, 28))
        self.buttonSet.setMaximumSize(QtCore.QSize(46, 28))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.buttonSet.setFont(font)
        self.buttonSet.setObjectName(_fromUtf8("buttonSet"))
        self.gridLayout2.addWidget(self.buttonSet, 1, 0, 1, 1)
        self.spinLayer = QtGui.QSpinBox(self.mainWidget)
        self.spinLayer.setAlignment(QtCore.Qt.AlignCenter)
        self.spinLayer.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.spinLayer.setSpecialValueText(_fromUtf8(""))
        self.spinLayer.setMinimum(1)
        self.spinLayer.setProperty("value", 1)
        self.spinLayer.setObjectName(_fromUtf8("spinLayer"))
        self.gridLayout2.addWidget(self.spinLayer, 0, 0, 1, 2)
        self.gridLayout_3.addLayout(self.gridLayout2, 0, 2, 2, 1)
        self.horizontalLayout1 = QtGui.QHBoxLayout()
        self.horizontalLayout1.setObjectName(_fromUtf8("horizontalLayout1"))
        self.buttonInitialize = QtGui.QPushButton(self.mainWidget)
        self.buttonInitialize.setEnabled(False)
        self.buttonInitialize.setMinimumSize(QtCore.QSize(93, 28))
        self.buttonInitialize.setMaximumSize(QtCore.QSize(93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.buttonInitialize.setFont(font)
        self.buttonInitialize.setObjectName(_fromUtf8("buttonInitialize"))
        self.horizontalLayout1.addWidget(self.buttonInitialize)
        self.buttonStart = QtGui.QPushButton(self.mainWidget)
        self.buttonStart.setEnabled(False)
        self.buttonStart.setMinimumSize(QtCore.QSize(93, 28))
        self.buttonStart.setMaximumSize(QtCore.QSize(93, 28))
        self.buttonStart.setObjectName(_fromUtf8("buttonStart"))
        self.horizontalLayout1.addWidget(self.buttonStart)
        self.buttonPause = QtGui.QPushButton(self.mainWidget)
        self.buttonPause.setEnabled(False)
        self.buttonPause.setMinimumSize(QtCore.QSize(93, 28))
        self.buttonPause.setMaximumSize(QtCore.QSize(93, 28))
        self.buttonPause.setObjectName(_fromUtf8("buttonPause"))
        self.horizontalLayout1.addWidget(self.buttonPause)
        self.buttonStop = QtGui.QPushButton(self.mainWidget)
        self.buttonStop.setEnabled(False)
        self.buttonStop.setMinimumSize(QtCore.QSize(93, 28))
        self.buttonStop.setMaximumSize(QtCore.QSize(93, 28))
        self.buttonStop.setObjectName(_fromUtf8("buttonStop"))
        self.horizontalLayout1.addWidget(self.buttonStop)
        self.gridLayout_3.addLayout(self.horizontalLayout1, 0, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 6, 0, 1, 1)
        self.checkSimulation = QtGui.QCheckBox(self.mainWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkSimulation.sizePolicy().hasHeightForWidth())
        self.checkSimulation.setSizePolicy(sizePolicy)
        self.checkSimulation.setMinimumSize(QtCore.QSize(121, 31))
        self.checkSimulation.setMaximumSize(QtCore.QSize(121, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.checkSimulation.setFont(font)
        self.checkSimulation.setChecked(True)
        self.checkSimulation.setObjectName(_fromUtf8("checkSimulation"))
        self.gridLayout_4.addWidget(self.checkSimulation, 2, 3, 1, 1)
        self.checkCleanup = QtGui.QCheckBox(self.mainWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.checkCleanup.setFont(font)
        self.checkCleanup.setChecked(True)
        self.checkCleanup.setObjectName(_fromUtf8("checkCleanup"))
        self.gridLayout_4.addWidget(self.checkCleanup, 3, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem1, 4, 3, 1, 1)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.buttonCameraCalibration = QtGui.QPushButton(self.mainWidget)
        self.buttonCameraCalibration.setObjectName(_fromUtf8("buttonCameraCalibration"))
        self.verticalLayout_3.addWidget(self.buttonCameraCalibration)
        self.buttonSliceConverter = QtGui.QPushButton(self.mainWidget)
        self.buttonSliceConverter.setObjectName(_fromUtf8("buttonSliceConverter"))
        self.verticalLayout_3.addWidget(self.buttonSliceConverter)
        self.gridLayout_4.addLayout(self.verticalLayout_3, 6, 3, 1, 1)
        self.widgetDisplay = QtGui.QTabWidget(self.mainWidget)
        self.widgetDisplay.setEnabled(True)
        self.widgetDisplay.setTabPosition(QtGui.QTabWidget.North)
        self.widgetDisplay.setTabShape(QtGui.QTabWidget.Rounded)
        self.widgetDisplay.setTabsClosable(False)
        self.widgetDisplay.setObjectName(_fromUtf8("widgetDisplay"))
        self.widgetTab1 = QtGui.QWidget()
        self.widgetTab1.setObjectName(_fromUtf8("widgetTab1"))
        self.gridLayout = QtGui.QGridLayout(self.widgetTab1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.labelDisplaySE = QtGui.QLabel(self.widgetTab1)
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.labelDisplaySE.setFont(font)
        self.labelDisplaySE.setScaledContents(True)
        self.labelDisplaySE.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDisplaySE.setObjectName(_fromUtf8("labelDisplaySE"))
        self.gridLayout.addWidget(self.labelDisplaySE, 0, 0, 2, 1)
        self.scrollSE = QtGui.QScrollBar(self.widgetTab1)
        self.scrollSE.setMinimum(1)
        self.scrollSE.setMaximum(1000)
        self.scrollSE.setOrientation(QtCore.Qt.Vertical)
        self.scrollSE.setInvertedAppearance(True)
        self.scrollSE.setInvertedControls(False)
        self.scrollSE.setObjectName(_fromUtf8("scrollSE"))
        self.gridLayout.addWidget(self.scrollSE, 0, 1, 2, 1)
        self.widgetDisplay.addTab(self.widgetTab1, _fromUtf8(""))
        self.widgetTab2 = QtGui.QWidget()
        self.widgetTab2.setObjectName(_fromUtf8("widgetTab2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.widgetTab2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.labelDisplayCE = QtGui.QLabel(self.widgetTab2)
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.labelDisplayCE.setFont(font)
        self.labelDisplayCE.setScaledContents(True)
        self.labelDisplayCE.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDisplayCE.setObjectName(_fromUtf8("labelDisplayCE"))
        self.gridLayout_2.addWidget(self.labelDisplayCE, 0, 0, 2, 1)
        self.scrollCE = QtGui.QScrollBar(self.widgetTab2)
        self.scrollCE.setMinimum(1)
        self.scrollCE.setMaximum(1000)
        self.scrollCE.setOrientation(QtCore.Qt.Vertical)
        self.scrollCE.setInvertedAppearance(True)
        self.scrollCE.setObjectName(_fromUtf8("scrollCE"))
        self.gridLayout_2.addWidget(self.scrollCE, 0, 1, 2, 1)
        self.widgetDisplay.addTab(self.widgetTab2, _fromUtf8(""))
        self.widgetTab3 = QtGui.QWidget()
        self.widgetTab3.setObjectName(_fromUtf8("widgetTab3"))
        self.gridLayout_5 = QtGui.QGridLayout(self.widgetTab3)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.labelDisplayDA = QtGui.QLabel(self.widgetTab3)
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.labelDisplayDA.setFont(font)
        self.labelDisplayDA.setScaledContents(True)
        self.labelDisplayDA.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDisplayDA.setWordWrap(True)
        self.labelDisplayDA.setObjectName(_fromUtf8("labelDisplayDA"))
        self.gridLayout_5.addWidget(self.labelDisplayDA, 0, 0, 2, 1)
        self.scrollDA = QtGui.QScrollBar(self.widgetTab3)
        self.scrollDA.setMinimum(1)
        self.scrollDA.setMaximum(1000)
        self.scrollDA.setOrientation(QtCore.Qt.Vertical)
        self.scrollDA.setInvertedAppearance(True)
        self.scrollDA.setObjectName(_fromUtf8("scrollDA"))
        self.gridLayout_5.addWidget(self.scrollDA, 0, 1, 2, 1)
        self.widgetDisplay.addTab(self.widgetTab3, _fromUtf8(""))
        self.widgetTab4 = QtGui.QWidget()
        self.widgetTab4.setObjectName(_fromUtf8("widgetTab4"))
        self.gridLayout_7 = QtGui.QGridLayout(self.widgetTab4)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.labelDisplayIV = QtGui.QLabel(self.widgetTab4)
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.labelDisplayIV.setFont(font)
        self.labelDisplayIV.setScaledContents(True)
        self.labelDisplayIV.setAlignment(QtCore.Qt.AlignCenter)
        self.labelDisplayIV.setWordWrap(True)
        self.labelDisplayIV.setObjectName(_fromUtf8("labelDisplayIV"))
        self.gridLayout_7.addWidget(self.labelDisplayIV, 0, 0, 2, 1)
        self.scrollIV = QtGui.QScrollBar(self.widgetTab4)
        self.scrollIV.setMinimum(1)
        self.scrollIV.setMaximum(1000)
        self.scrollIV.setProperty("value", 1)
        self.scrollIV.setOrientation(QtCore.Qt.Vertical)
        self.scrollIV.setInvertedAppearance(True)
        self.scrollIV.setObjectName(_fromUtf8("scrollIV"))
        self.gridLayout_7.addWidget(self.scrollIV, 0, 1, 2, 1)
        self.widgetDisplay.addTab(self.widgetTab4, _fromUtf8(""))
        self.gridLayout_4.addWidget(self.widgetDisplay, 0, 0, 6, 3)
        mainWindow.setCentralWidget(self.mainWidget)
        self.menuBar = QtGui.QMenuBar(mainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1209, 26))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSetup = QtGui.QMenu(self.menuBar)
        self.menuSetup.setObjectName(_fromUtf8("menuSetup"))
        self.menuReportSettings = QtGui.QMenu(self.menuSetup)
        self.menuReportSettings.setObjectName(_fromUtf8("menuReportSettings"))
        self.menuRun = QtGui.QMenu(self.menuBar)
        self.menuRun.setObjectName(_fromUtf8("menuRun"))
        mainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtGui.QStatusBar(mainWindow)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.statusBar.setFont(font)
        self.statusBar.setStatusTip(_fromUtf8(""))
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        mainWindow.setStatusBar(self.statusBar)
        self.actionConfigurationSettings = QtGui.QAction(mainWindow)
        self.actionConfigurationSettings.setObjectName(_fromUtf8("actionConfigurationSettings"))
        self.actionCLS = QtGui.QAction(mainWindow)
        self.actionCLS.setObjectName(_fromUtf8("actionCLS"))
        self.actionCLI = QtGui.QAction(mainWindow)
        self.actionCLI.setEnabled(False)
        self.actionCLI.setObjectName(_fromUtf8("actionCLI"))
        self.actionNewBuild = QtGui.QAction(mainWindow)
        self.actionNewBuild.setObjectName(_fromUtf8("actionNewBuild"))
        self.actionOpenBuild = QtGui.QAction(mainWindow)
        self.actionOpenBuild.setObjectName(_fromUtf8("actionOpenBuild"))
        self.actionExportImage = QtGui.QAction(mainWindow)
        self.actionExportImage.setEnabled(False)
        self.actionExportImage.setObjectName(_fromUtf8("actionExportImage"))
        self.actionError_actions = QtGui.QAction(mainWindow)
        self.actionError_actions.setObjectName(_fromUtf8("actionError_actions"))
        self.actionDefectActions = QtGui.QAction(mainWindow)
        self.actionDefectActions.setObjectName(_fromUtf8("actionDefectActions"))
        self.actionNotificationSettings = QtGui.QAction(mainWindow)
        self.actionNotificationSettings.setObjectName(_fromUtf8("actionNotificationSettings"))
        self.actionAdjustCrop = QtGui.QAction(mainWindow)
        self.actionAdjustCrop.setObjectName(_fromUtf8("actionAdjustCrop"))
        self.actionAdjustRotation = QtGui.QAction(mainWindow)
        self.actionAdjustRotation.setObjectName(_fromUtf8("actionAdjustRotation"))
        self.actionStartBuild = QtGui.QAction(mainWindow)
        self.actionStartBuild.setEnabled(False)
        self.actionStartBuild.setObjectName(_fromUtf8("actionStartBuild"))
        self.actionPauseBuild = QtGui.QAction(mainWindow)
        self.actionPauseBuild.setEnabled(False)
        self.actionPauseBuild.setObjectName(_fromUtf8("actionPauseBuild"))
        self.actionStopBuild = QtGui.QAction(mainWindow)
        self.actionStopBuild.setEnabled(False)
        self.actionStopBuild.setObjectName(_fromUtf8("actionStopBuild"))
        self.actionExit = QtGui.QAction(mainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionInitializeBuild = QtGui.QAction(mainWindow)
        self.actionInitializeBuild.setEnabled(False)
        self.actionInitializeBuild.setObjectName(_fromUtf8("actionInitializeBuild"))
        self.actionDefectProcessing = QtGui.QAction(mainWindow)
        self.actionDefectProcessing.setEnabled(False)
        self.actionDefectProcessing.setObjectName(_fromUtf8("actionDefectProcessing"))
        self.actionCameraCalibration = QtGui.QAction(mainWindow)
        self.actionCameraCalibration.setObjectName(_fromUtf8("actionCameraCalibration"))
        self.actionSliceConverter = QtGui.QAction(mainWindow)
        self.actionSliceConverter.setObjectName(_fromUtf8("actionSliceConverter"))
        self.actionCameraSettings = QtGui.QAction(mainWindow)
        self.actionCameraSettings.setObjectName(_fromUtf8("actionCameraSettings"))
        self.menuFile.addAction(self.actionNewBuild)
        self.menuFile.addAction(self.actionOpenBuild)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExportImage)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuReportSettings.addAction(self.actionDefectActions)
        self.menuReportSettings.addAction(self.actionNotificationSettings)
        self.menuSetup.addAction(self.actionConfigurationSettings)
        self.menuSetup.addAction(self.actionCameraSettings)
        self.menuSetup.addSeparator()
        self.menuSetup.addAction(self.actionCameraCalibration)
        self.menuSetup.addAction(self.actionSliceConverter)
        self.menuSetup.addSeparator()
        self.menuSetup.addAction(self.menuReportSettings.menuAction())
        self.menuRun.addAction(self.actionInitializeBuild)
        self.menuRun.addAction(self.actionStartBuild)
        self.menuRun.addAction(self.actionPauseBuild)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionStopBuild)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionDefectProcessing)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuSetup.menuAction())
        self.menuBar.addAction(self.menuRun.menuAction())

        self.retranslateUi(mainWindow)
        self.widgetDisplay.setCurrentIndex(0)
        QtCore.QObject.connect(self.widgetDisplay, QtCore.SIGNAL(_fromUtf8("currentChanged(int)")), mainWindow.update)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "Defect Monitor", None))
        self.groupPositionAdjustment.setTitle(_translate("mainWindow", "Position Adjustment", None))
        self.buttonCrop.setToolTip(_translate("mainWindow", "Click to move the crop boundary.", None))
        self.buttonCrop.setText(_translate("mainWindow", "╬", None))
        self.buttonShiftLeft.setToolTip(_translate("mainWindow", "Shifts the display image left by the given pixels.", None))
        self.buttonShiftLeft.setText(_translate("mainWindow", "◄", None))
        self.buttonShiftRight.setToolTip(_translate("mainWindow", "Shifts the display image right by the given pixels.", None))
        self.buttonShiftRight.setText(_translate("mainWindow", "►", None))
        self.buttonShiftDown.setToolTip(_translate("mainWindow", "Shifts the display image down by the given pixels.", None))
        self.buttonShiftDown.setText(_translate("mainWindow", "▼", None))
        self.buttonShiftUp.setToolTip(_translate("mainWindow", "Shifts the display image up by the given pixels.", None))
        self.buttonShiftUp.setText(_translate("mainWindow", "▲", None))
        self.buttonRotateACW.setToolTip(_translate("mainWindow", "Clocwise rotates the display image by the given degrees.", None))
        self.buttonRotateACW.setText(_translate("mainWindow", "↺", None))
        self.buttonRotateCW.setToolTip(_translate("mainWindow", "Anti-Clocwise rotates the display image by the given degrees.", None))
        self.buttonRotateCW.setText(_translate("mainWindow", "↻", None))
        self.labelPixels.setText(_translate("mainWindow", "Pixels", None))
        self.buttonBoundary.setToolTip(_translate("mainWindow", "Click to move the overlay boundary.", None))
        self.buttonBoundary.setText(_translate("mainWindow", "□", None))
        self.lineShiftDegrees.setText(_translate("mainWindow", "0.05", None))
        self.lineShiftPixels.setText(_translate("mainWindow", "1", None))
        self.labelDegrees.setText(_translate("mainWindow", "Degrees", None))
        self.groupOpenCV.setTitle(_translate("mainWindow", "OpenCV Processing", None))
        self.radioOpenCV1.setText(_translate("mainWindow", "Test Code 1", None))
        self.radioOpenCV2.setText(_translate("mainWindow", "Test Code 2", None))
        self.radioOpenCV3.setText(_translate("mainWindow", "Test Code 3", None))
        self.radioOpenCV4.setText(_translate("mainWindow", "Test Code 4", None))
        self.radioOpenCV5.setText(_translate("mainWindow", "Test Code 5", None))
        self.groupDisplayOptions.setTitle(_translate("mainWindow", "Display Options", None))
        self.radioRaw.setText(_translate("mainWindow", "Raw Image", None))
        self.radioCorrection.setText(_translate("mainWindow", "Correction", None))
        self.radioCrop.setText(_translate("mainWindow", "Crop to Size", None))
        self.radioCLAHE.setText(_translate("mainWindow", "Equalization", None))
        self.checkToggleOverlay.setText(_translate("mainWindow", "Toggle Overlay", None))
        self.buttonImageConverter.setToolTip(_translate("mainWindow", "Click to select an image to run the image correction processes.", None))
        self.buttonImageConverter.setText(_translate("mainWindow", "Image Converter", None))
        self.buttonDefectProcessing.setToolTip(_translate("mainWindow", "Click to process the currently displayed image using OpenCV for defects.", None))
        self.buttonDefectProcessing.setText(_translate("mainWindow", "Analyze for Defects", None))
        self.buttonImageCapture.setToolTip(_translate("mainWindow", "Click to open the tool to capture images from an attached camera.", None))
        self.buttonImageCapture.setText(_translate("mainWindow", "Image Capture", None))
        self.buttonNotificationSettings.setText(_translate("mainWindow", "Notification Settings", None))
        self.buttonDisplayImages.setText(_translate("mainWindow", "Display Images", None))
        self.labelLayerNumberTitle.setText(_translate("mainWindow", "<html><head/><body><p align=\"center\">Layer Number</p></body></html>", None))
        self.labelLayerNumber.setText(_translate("mainWindow", "0001", None))
        self.buttonSet.setText(_translate("mainWindow", "SET", None))
        self.buttonInitialize.setText(_translate("mainWindow", "Initialize", None))
        self.buttonStart.setText(_translate("mainWindow", "Start", None))
        self.buttonPause.setText(_translate("mainWindow", "Pause", None))
        self.buttonStop.setText(_translate("mainWindow", "Stop", None))
        self.checkSimulation.setToolTip(_translate("mainWindow", "Check to use and process pre-taken sample images from the samples folder.", None))
        self.checkSimulation.setText(_translate("mainWindow", "Simulation", None))
        self.checkCleanup.setToolTip(_translate("mainWindow", "Check to delete all created folders (and their contents) upon closing the program.", None))
        self.checkCleanup.setText(_translate("mainWindow", "Cleanup", None))
        self.buttonCameraCalibration.setToolTip(_translate("mainWindow", "Click to select a folder of images to perform camera calibration with.", None))
        self.buttonCameraCalibration.setText(_translate("mainWindow", "Camera Calibration", None))
        self.buttonSliceConverter.setToolTip(_translate("mainWindow", "Click to select a slice file to convert into ASCII encoding.", None))
        self.buttonSliceConverter.setText(_translate("mainWindow", "Slice Converter", None))
        self.labelDisplaySE.setText(_translate("mainWindow", "File -> New Build -> OK -> Initialize", None))
        self.widgetDisplay.setTabText(self.widgetDisplay.indexOf(self.widgetTab1), _translate("mainWindow", "Scan Explorer", None))
        self.labelDisplayCE.setText(_translate("mainWindow", "File -> New Build -> OK -> Initialize", None))
        self.widgetDisplay.setTabText(self.widgetDisplay.indexOf(self.widgetTab2), _translate("mainWindow", "Coat Explorer", None))
        self.labelDisplayDA.setText(_translate("mainWindow", "File -> New Build -> OK -> Initialize -> On Scan or Coat Tab -> Analyze for Defects", None))
        self.widgetDisplay.setTabText(self.widgetDisplay.indexOf(self.widgetTab3), _translate("mainWindow", "Defect Analyzer", None))
        self.labelDisplayIV.setText(_translate("mainWindow", "Image Capture > Run", None))
        self.widgetDisplay.setTabText(self.widgetDisplay.indexOf(self.widgetTab4), _translate("mainWindow", "Image Viewer", None))
        self.menuFile.setTitle(_translate("mainWindow", "File", None))
        self.menuSetup.setTitle(_translate("mainWindow", "Setup", None))
        self.menuReportSettings.setTitle(_translate("mainWindow", "Report Settings", None))
        self.menuRun.setTitle(_translate("mainWindow", "Run", None))
        self.actionConfigurationSettings.setText(_translate("mainWindow", "Configuration Settings", None))
        self.actionCLS.setText(_translate("mainWindow", "CLS", None))
        self.actionCLI.setText(_translate("mainWindow", "CLI", None))
        self.actionNewBuild.setText(_translate("mainWindow", "New Build...", None))
        self.actionOpenBuild.setText(_translate("mainWindow", "Open Build...", None))
        self.actionExportImage.setText(_translate("mainWindow", "Export Image...", None))
        self.actionExportImage.setToolTip(_translate("mainWindow", "Exports the currently displayed image to the selected folder.", None))
        self.actionError_actions.setText(_translate("mainWindow", "Defect actions", None))
        self.actionDefectActions.setText(_translate("mainWindow", "Defect Actions", None))
        self.actionNotificationSettings.setText(_translate("mainWindow", "Notification Setup", None))
        self.actionAdjustCrop.setText(_translate("mainWindow", "Adjust Crop", None))
        self.actionAdjustRotation.setText(_translate("mainWindow", "Adjust Rotation", None))
        self.actionStartBuild.setText(_translate("mainWindow", "Start Build", None))
        self.actionPauseBuild.setText(_translate("mainWindow", "Pause Build", None))
        self.actionStopBuild.setText(_translate("mainWindow", "Stop Build", None))
        self.actionExit.setText(_translate("mainWindow", "Exit", None))
        self.actionInitializeBuild.setText(_translate("mainWindow", "Initialize Build", None))
        self.actionDefectProcessing.setText(_translate("mainWindow", "Analyze for Defects", None))
        self.actionCameraCalibration.setText(_translate("mainWindow", "Camera Calibration", None))
        self.actionSliceConverter.setText(_translate("mainWindow", "Slice Converter", None))
        self.actionCameraSettings.setText(_translate("mainWindow", "Camera Settings", None))

import icons_rc
