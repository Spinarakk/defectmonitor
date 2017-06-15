@echo off
d:
cd "D:\Documents\MCAM\Defect Monitor\gui"
pyrcc4 -o icons_rc.py icons.qrc && pyuic4 -o mainWindow.py mainWindow.ui && pyuic4 -o dialogNewBuild.py dialogNewBuild.ui