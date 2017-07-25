@echo off
set mypath=%cd%
cd "%mypath%\gui"
pyrcc4 -o icons_rc.py icons.qrc && pyuic4 -o mainWindow.py mainWindow.ui && pyuic4 -o dialogNewBuild.py dialogNewBuild.ui && pyuic4 -o dialogCameraCalibration.py dialogCameraCalibration.ui && pyuic4 -o dialogCalibrationResults.py dialogCalibrationResults.ui && pyuic4 -o dialogSliceConverter.py dialogSliceConverter.ui && pyuic4 -o dialogImageCapture.py dialogImageCapture.ui && pyuic4 -o dialogCameraSettings.py dialogCameraSettings.ui