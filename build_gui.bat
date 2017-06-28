@echo off
set mypath=%cd%
cd "%mypath%\gui"
pyrcc4 -o icons_rc.py icons.qrc && pyuic4 -o mainWindow.py mainWindow.ui && pyuic4 -o dialogNewBuild.py dialogNewBuild.ui && pyuic4 -o dialogCameraCalibration.py dialogCameraCalibration.ui