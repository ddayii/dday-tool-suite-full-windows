@echo off
setlocal
cd /d "%~dp0"

echo.
echo Building DDay Controls FANUC I/O Tool...
pyinstaller --noconfirm --clean fanuc_io_tool.spec
if errorlevel 1 goto :error

echo.
echo Build complete.
echo EXE is in the dist folder:
echo   dist\DDay Controls FANUC IO Tool.exe
echo.
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
