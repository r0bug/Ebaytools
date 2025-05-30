@echo off
title eBay Tools - Viewer
cd /d "%~dp0"
set PYTHONPATH=%~dp0;%PYTHONPATH%

echo Starting eBay Tools - Viewer...
echo.

:: Try different Python commands
python --version >nul 2>&1
if %errorlevel% == 0 (
    python -m ebay_tools.apps.viewer
    goto :end
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    py -m ebay_tools.apps.viewer
    goto :end
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    python3 -m ebay_tools.apps.viewer
    goto :end
)

echo Python not found! Please run install.bat first.
pause

:end
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Check the logs folder for details.
    pause
)