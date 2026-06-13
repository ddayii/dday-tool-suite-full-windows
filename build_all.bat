@echo off
setlocal
cd /d "%~dp0"

echo Building DDay Controls Conversion Tool...
pyinstaller --noconfirm --clean converter_tool.spec
if errorlevel 1 goto :error

echo.
echo Building DDay Controls ASCII Chart...
pyinstaller --noconfirm --clean ascii_chart.spec
if errorlevel 1 goto :error

echo.
echo Building DDay Controls FANUC I/O Tool...
pyinstaller --noconfirm --clean fanuc_io_tool.spec
if errorlevel 1 goto :error

echo.
echo Building DDay Controls Tool Suite Launcher...
pyinstaller --noconfirm --clean launcher.spec
if errorlevel 1 goto :error

echo.
echo Build complete.
echo EXEs are in the dist folder:
echo   dist\DDay Controls Tool Suite.exe
echo   dist\DDay Controls Conversion Tool.exe
echo   dist\DDay Controls ASCII Chart.exe
echo   dist\DDay Controls FANUC IO Tool.exe
echo.
echo To build the installer, compile installer.iss with Inno Setup:
echo   https://jrsoftware.org/isinfo.php
echo   Output: installer\DDay Controls Tool Suite Setup 2.1.1.exe
echo.
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
