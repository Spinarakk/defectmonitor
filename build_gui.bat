@echo off
d:
cd "D:\Documents\MCAM\Defect Monitor\gui"
pyuic4 -o mainWindow.py mainWindow.ui && pyuic4 -o dialogNewBuild.py dialogNewBuild.ui