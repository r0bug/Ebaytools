@echo off
:: eBay Tools Dependency Installer for Windows
:: Comprehensive Windows installation script

title eBay Tools Dependency Installer
color 0A

echo.
echo =============================================
echo    eBay Tools Dependency Installer v3.0.0
echo =============================================
echo Platform: Windows
echo.

set "PYTHON_CMD="
set "INSTALL_SUCCESS=1"

:: Check for Python installation
echo Detecting Python installation...
echo.

:: Try python command first
python --version >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=python"
    echo [OK] Found Python using 'python' command
    python --version
    goto :check_version
)

:: Try py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=py"
    echo [OK] Found Python using 'py' launcher
    py --version
    goto :check_version
)

:: Try python3
python3 --version >nul 2>&1
if %errorlevel% == 0 (
    set "PYTHON_CMD=python3"
    echo [OK] Found Python using 'python3' command
    python3 --version
    goto :check_version
)

echo [ERROR] Python not found!
echo.
echo Python 3.8 or higher is required for eBay Tools.
echo Please download and install Python from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: During installation, make sure to check
echo "Add Python to PATH" option.
echo.
echo Opening download page...
start https://www.python.org/downloads/
echo.
pause
exit /b 1

:check_version
echo.
echo Checking Python version compatibility...
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8 or higher is required!
    echo Current version is too old. Please update Python.
    pause
    exit /b 1
)
echo [OK] Python version is compatible
echo.

:: Check pip
echo Checking pip availability...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available!
    echo Please ensure pip is installed with Python.
    set "INSTALL_SUCCESS=0"
    goto :summary
)
echo [OK] pip is available
echo.

:: Upgrade pip
echo Upgrading pip to latest version...
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing...
)
echo.

:: Install core dependencies
echo Installing core dependencies...
echo This may take a few minutes...
echo.

echo Installing requests...
%PYTHON_CMD% -m pip install "requests>=2.25.1"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requests
    set "INSTALL_SUCCESS=0"
)

echo Installing Pillow (image processing)...
%PYTHON_CMD% -m pip install "pillow>=8.2.0"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Pillow
    set "INSTALL_SUCCESS=0"
)

echo Installing BeautifulSoup4 (HTML parsing)...
%PYTHON_CMD% -m pip install "beautifulsoup4>=4.9.3"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install BeautifulSoup4
    set "INSTALL_SUCCESS=0"
)

:: Install optional dependencies
echo.
echo Installing optional dependencies...

echo Installing lxml (faster parsing)...
%PYTHON_CMD% -m pip install lxml
if %errorlevel% neq 0 (
    echo [WARNING] lxml installation failed (optional)
)

echo Installing numpy (numerical operations)...
%PYTHON_CMD% -m pip install numpy
if %errorlevel% neq 0 (
    echo [WARNING] numpy installation failed (optional)
)

echo Installing certifi (SSL certificates)...
%PYTHON_CMD% -m pip install certifi
if %errorlevel% neq 0 (
    echo [WARNING] certifi installation failed (optional)
)

:: Test imports
echo.
echo Testing critical imports...
echo.

echo Testing tkinter GUI framework...
%PYTHON_CMD% -c "import tkinter; print('✓ tkinter working')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] tkinter not working - GUI will not function
    echo Try reinstalling Python with tkinter support
    set "INSTALL_SUCCESS=0"
) else (
    echo [OK] tkinter working
)

echo Testing requests HTTP library...
%PYTHON_CMD% -c "import requests; print('✓ requests working')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] requests not working
    set "INSTALL_SUCCESS=0"
) else (
    echo [OK] requests working
)

echo Testing Pillow image processing...
%PYTHON_CMD% -c "from PIL import Image; print('✓ Pillow working')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Pillow not working
    set "INSTALL_SUCCESS=0"
) else (
    echo [OK] Pillow working
)

echo Testing BeautifulSoup HTML parsing...
%PYTHON_CMD% -c "from bs4 import BeautifulSoup; print('✓ BeautifulSoup working')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] BeautifulSoup not working
    set "INSTALL_SUCCESS=0"
) else (
    echo [OK] BeautifulSoup working
)

:summary
echo.
echo =============================================
echo    Installation Summary
echo =============================================

if "%INSTALL_SUCCESS%"=="1" (
    echo.
    echo [SUCCESS] All dependencies installed successfully!
    echo.
    echo Your system is ready to run eBay Tools.
    echo.
    echo Next steps:
    echo 1. Extract the eBay Tools package
    echo 2. Run the applications using batch files
    echo 3. Configure API keys in application settings
    echo.
    echo Applications you can run:
    echo - ebay_setup.bat       (Setup and queue management)
    echo - ebay_processor.bat   (AI photo processing)
    echo - ebay_viewer.bat      (Review and export)
    echo - ebay_price.bat       (Price analysis)
    echo.
) else (
    echo.
    echo [ERROR] Installation completed with errors!
    echo.
    echo Some dependencies failed to install. eBay Tools may not
    echo function correctly. Please check the error messages above
    echo and try to resolve them.
    echo.
    echo Common solutions:
    echo - Restart command prompt as Administrator
    echo - Check internet connection
    echo - Update Python to latest version
    echo - Reinstall Python with all components
    echo.
)

echo =============================================
echo.
pause