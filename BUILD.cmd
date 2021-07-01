@ECHO OFF 
:: This batch file creates ADCSee sorter executable file
TITLE ADCSee sorter executable file builder
ECHO ADCSee sorter executable file builder
ECHO -------------------------------------
ECHO WARNING! Please make sure you have installed: 
ECHO	- python3.8+
ECHO	- win32gui (pip install win32gui)
ECHO	- pyinstaller (pip install pyinstaller)
ECHO.
PAUSE
ECHO.
ECHO Compiling... 
ECHO -------------------------------------
pyinstaller --onefile --name=_adcsee-sorter_0.1.0.exe acdsee_sorter.py
ECHO.
ECHO If no errors were encountered while building, the executable file is located in the /dist folder
PAUSE