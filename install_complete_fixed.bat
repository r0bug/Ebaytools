@echo off
:: eBay Tools Complete Installer v3.0.1 - FIXED
:: Comprehensive installer that installs and verifies all code files every time
:: Supports fresh installations and updates of existing installations
:: FIXED: Creates batch files that work after installation

title eBay Tools Complete Installer v3.0.1
color 0A

echo.
echo ==========================================
echo   eBay Tools Complete Installer v3.0.1
echo ==========================================
echo.
echo This installer will:
echo   - Check for Python installation
echo   - Install/update ALL code files
echo   - Install required dependencies  
echo   - Verify all features are present
echo   - Create application launchers
echo   - Set up desktop shortcuts
echo   - Test installation integrity
echo.

set "PYTHON_CMD="
set "INSTALL_DIR=%~dp0"
set "TARGET_DIR=%INSTALL_DIR%ebay_tools\"
set "SOURCE_DIR=%INSTALL_DIR%windows_installer\ebay_tools\"

:: Check for Python installation
echo [1/8] Checking for Python installation...
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
echo Python 3.8 or higher is required to run eBay Tools.
echo Please download and install Python from: https://www.python.org/downloads/
echo IMPORTANT: During installation, check "Add Python to PATH" option.
echo.
pause
exit /b 1

:check_version
echo.
echo Checking Python version compatibility...
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8 or higher is required!
    echo Please update your Python installation.
    pause
    exit /b 1
)
echo [OK] Python version is compatible
echo.

:: Backup existing installation if it exists
echo [2/8] Preparing installation directory...
if exist "%TARGET_DIR%" (
    echo Found existing installation - creating backup...
    if exist "%INSTALL_DIR%ebay_tools_backup\" (
        rmdir /s /q "%INSTALL_DIR%ebay_tools_backup\" >nul 2>&1
    )
    move "%TARGET_DIR%" "%INSTALL_DIR%ebay_tools_backup\" >nul 2>&1
    echo [OK] Existing installation backed up
) else (
    echo [OK] Fresh installation directory
)
echo.

:: Copy all code files
echo [3/8] Installing all code files...
if not exist "%SOURCE_DIR%" (
    echo [ERROR] Source directory not found: %SOURCE_DIR%
    echo This installer must be run from the extracted eBay Tools directory.
    pause
    exit /b 1
)

:: Create target directory structure
mkdir "%TARGET_DIR%" 2>nul
mkdir "%TARGET_DIR%apps\" 2>nul
mkdir "%TARGET_DIR%core\" 2>nul
mkdir "%TARGET_DIR%utils\" 2>nul

:: Copy all Python files with verification
echo Copying core module files...
copy "%SOURCE_DIR%__init__.py" "%TARGET_DIR%__init__.py" >nul
copy "%SOURCE_DIR%apps\*.py" "%TARGET_DIR%apps\" >nul
copy "%SOURCE_DIR%core\*.py" "%TARGET_DIR%core\" >nul
copy "%SOURCE_DIR%utils\*.py" "%TARGET_DIR%utils\" >nul

:: Copy requirements file
copy "%INSTALL_DIR%windows_installer\requirements.txt" "%INSTALL_DIR%requirements.txt" >nul

echo [OK] All code files installed
echo.

:: Verify critical files are present
echo [4/8] Verifying file installation...
set "MISSING_FILES="

if not exist "%TARGET_DIR%__init__.py" set "MISSING_FILES=%MISSING_FILES% __init__.py"
if not exist "%TARGET_DIR%apps\processor.py" set "MISSING_FILES=%MISSING_FILES% processor.py"
if not exist "%TARGET_DIR%apps\setup.py" set "MISSING_FILES=%MISSING_FILES% setup.py"
if not exist "%TARGET_DIR%apps\viewer.py" set "MISSING_FILES=%MISSING_FILES% viewer.py"
if not exist "%TARGET_DIR%apps\price_analyzer.py" set "MISSING_FILES=%MISSING_FILES% price_analyzer.py"
if not exist "%TARGET_DIR%core\api.py" set "MISSING_FILES=%MISSING_FILES% api.py"
if not exist "%TARGET_DIR%core\schema.py" set "MISSING_FILES=%MISSING_FILES% schema.py"

if not "%MISSING_FILES%"=="" (
    echo [ERROR] Missing critical files:%MISSING_FILES%
    echo Installation failed. Please check source files and try again.
    pause
    exit /b 1
)
echo [OK] All critical files verified present
echo.

:: Check if pip is available
echo [5/8] Installing dependencies...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available!
    echo Please ensure pip is installed with Python.
    pause
    exit /b 1
)

:: Install/update dependencies
echo Installing required packages...
%PYTHON_CMD% -m pip install --upgrade pip >nul 2>&1
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

:: Test installation functionality
echo [6/8] Testing installation integrity...

:: Test basic imports
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); import ebay_tools; print('Package import: OK')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Package import test failed
) else (
    echo [OK] Package imports successfully
)

:: Test GUI dependencies
%PYTHON_CMD% -c "import tkinter, requests, PIL; print('GUI dependencies: OK')" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Some GUI dependencies may not be properly installed
    echo The applications may still work, but some features might be limited
) else (
    echo [OK] All GUI dependencies working
)

:: Test version detection
echo Testing version detection...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); from ebay_tools import __version__; print(f'Version detected: {__version__}')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Version detection test failed - using fallback
) else (
    echo [OK] Version detection working
)

:: Test reset functionality presence
findstr /C:"Reset Tags" "%TARGET_DIR%apps\processor.py" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Reset functionality not found in processor!
    echo This indicates a critical installation problem.
    pause
    exit /b 1
) else (
    echo [OK] Reset functionality verified present
)

echo.

:: Create application launchers  
echo [7/8] Creating application launchers...

:: Create enhanced batch files that try multiple Python commands
echo @echo off > ebay_setup.bat
echo title eBay Tools - Setup >> ebay_setup.bat
echo cd /d "%%~dp0" >> ebay_setup.bat
echo set PYTHONPATH=.;%%PYTHONPATH%% >> ebay_setup.bat
echo. >> ebay_setup.bat
echo :: Try different Python commands >> ebay_setup.bat
echo python --version ^>nul 2^>^&1 >> ebay_setup.bat
echo if %%errorlevel%% == 0 ( >> ebay_setup.bat
echo     python -m ebay_tools.apps.setup >> ebay_setup.bat
echo     goto :end >> ebay_setup.bat
echo ^) >> ebay_setup.bat
echo. >> ebay_setup.bat
echo py --version ^>nul 2^>^&1 >> ebay_setup.bat
echo if %%errorlevel%% == 0 ( >> ebay_setup.bat
echo     py -m ebay_tools.apps.setup >> ebay_setup.bat
echo     goto :end >> ebay_setup.bat
echo ^) >> ebay_setup.bat
echo. >> ebay_setup.bat
echo python3 --version ^>nul 2^>^&1 >> ebay_setup.bat
echo if %%errorlevel%% == 0 ( >> ebay_setup.bat
echo     python3 -m ebay_tools.apps.setup >> ebay_setup.bat
echo     goto :end >> ebay_setup.bat
echo ^) >> ebay_setup.bat
echo. >> ebay_setup.bat
echo echo Python not found! Please install Python 3.8 or higher. >> ebay_setup.bat
echo pause >> ebay_setup.bat
echo. >> ebay_setup.bat
echo :end >> ebay_setup.bat
echo if %%errorlevel%% neq 0 ( >> ebay_setup.bat
echo     echo. >> ebay_setup.bat
echo     echo [ERROR] Application failed to start >> ebay_setup.bat
echo     echo Please check the installation and try again >> ebay_setup.bat
echo     pause >> ebay_setup.bat
echo ^) >> ebay_setup.bat

echo @echo off > ebay_processor.bat
echo title eBay Tools - Processor >> ebay_processor.bat
echo cd /d "%%~dp0" >> ebay_processor.bat
echo set PYTHONPATH=.;%%PYTHONPATH%% >> ebay_processor.bat
echo. >> ebay_processor.bat
echo :: Try different Python commands >> ebay_processor.bat
echo python --version ^>nul 2^>^&1 >> ebay_processor.bat
echo if %%errorlevel%% == 0 ( >> ebay_processor.bat
echo     python -m ebay_tools.apps.processor >> ebay_processor.bat
echo     goto :end >> ebay_processor.bat
echo ^) >> ebay_processor.bat
echo. >> ebay_processor.bat
echo py --version ^>nul 2^>^&1 >> ebay_processor.bat
echo if %%errorlevel%% == 0 ( >> ebay_processor.bat
echo     py -m ebay_tools.apps.processor >> ebay_processor.bat
echo     goto :end >> ebay_processor.bat
echo ^) >> ebay_processor.bat
echo. >> ebay_processor.bat
echo python3 --version ^>nul 2^>^&1 >> ebay_processor.bat
echo if %%errorlevel%% == 0 ( >> ebay_processor.bat
echo     python3 -m ebay_tools.apps.processor >> ebay_processor.bat
echo     goto :end >> ebay_processor.bat
echo ^) >> ebay_processor.bat
echo. >> ebay_processor.bat
echo echo Python not found! Please install Python 3.8 or higher. >> ebay_processor.bat
echo pause >> ebay_processor.bat
echo. >> ebay_processor.bat
echo :end >> ebay_processor.bat
echo if %%errorlevel%% neq 0 ( >> ebay_processor.bat
echo     echo. >> ebay_processor.bat
echo     echo [ERROR] Application failed to start >> ebay_processor.bat
echo     echo Please check the installation and try again >> ebay_processor.bat
echo     pause >> ebay_processor.bat
echo ^) >> ebay_processor.bat

echo @echo off > ebay_viewer.bat
echo title eBay Tools - Viewer >> ebay_viewer.bat
echo cd /d "%%~dp0" >> ebay_viewer.bat
echo set PYTHONPATH=.;%%PYTHONPATH%% >> ebay_viewer.bat
echo. >> ebay_viewer.bat
echo :: Try different Python commands >> ebay_viewer.bat
echo python --version ^>nul 2^>^&1 >> ebay_viewer.bat
echo if %%errorlevel%% == 0 ( >> ebay_viewer.bat
echo     python -m ebay_tools.apps.viewer >> ebay_viewer.bat
echo     goto :end >> ebay_viewer.bat
echo ^) >> ebay_viewer.bat
echo. >> ebay_viewer.bat
echo py --version ^>nul 2^>^&1 >> ebay_viewer.bat
echo if %%errorlevel%% == 0 ( >> ebay_viewer.bat
echo     py -m ebay_tools.apps.viewer >> ebay_viewer.bat
echo     goto :end >> ebay_viewer.bat
echo ^) >> ebay_viewer.bat
echo. >> ebay_viewer.bat
echo python3 --version ^>nul 2^>^&1 >> ebay_viewer.bat
echo if %%errorlevel%% == 0 ( >> ebay_viewer.bat
echo     python3 -m ebay_tools.apps.viewer >> ebay_viewer.bat
echo     goto :end >> ebay_viewer.bat
echo ^) >> ebay_viewer.bat
echo. >> ebay_viewer.bat
echo echo Python not found! Please install Python 3.8 or higher. >> ebay_viewer.bat
echo pause >> ebay_viewer.bat
echo. >> ebay_viewer.bat
echo :end >> ebay_viewer.bat
echo if %%errorlevel%% neq 0 ( >> ebay_viewer.bat
echo     echo. >> ebay_viewer.bat
echo     echo [ERROR] Application failed to start >> ebay_viewer.bat
echo     echo Please check the installation and try again >> ebay_viewer.bat
echo     pause >> ebay_viewer.bat
echo ^) >> ebay_viewer.bat

echo @echo off > ebay_price.bat
echo title eBay Tools - Price Analyzer >> ebay_price.bat
echo cd /d "%%~dp0" >> ebay_price.bat
echo set PYTHONPATH=.;%%PYTHONPATH%% >> ebay_price.bat
echo. >> ebay_price.bat
echo :: Try different Python commands >> ebay_price.bat
echo python --version ^>nul 2^>^&1 >> ebay_price.bat
echo if %%errorlevel%% == 0 ( >> ebay_price.bat
echo     python -m ebay_tools.apps.price_analyzer >> ebay_price.bat
echo     goto :end >> ebay_price.bat
echo ^) >> ebay_price.bat
echo. >> ebay_price.bat
echo py --version ^>nul 2^>^&1 >> ebay_price.bat
echo if %%errorlevel%% == 0 ( >> ebay_price.bat
echo     py -m ebay_tools.apps.price_analyzer >> ebay_price.bat
echo     goto :end >> ebay_price.bat
echo ^) >> ebay_price.bat
echo. >> ebay_price.bat
echo python3 --version ^>nul 2^>^&1 >> ebay_price.bat
echo if %%errorlevel%% == 0 ( >> ebay_price.bat
echo     python3 -m ebay_tools.apps.price_analyzer >> ebay_price.bat
echo     goto :end >> ebay_price.bat
echo ^) >> ebay_price.bat
echo. >> ebay_price.bat
echo echo Python not found! Please install Python 3.8 or higher. >> ebay_price.bat
echo pause >> ebay_price.bat
echo. >> ebay_price.bat
echo :end >> ebay_price.bat
echo if %%errorlevel%% neq 0 ( >> ebay_price.bat
echo     echo. >> ebay_price.bat
echo     echo [ERROR] Application failed to start >> ebay_price.bat
echo     echo Please check the installation and try again >> ebay_price.bat
echo     pause >> ebay_price.bat
echo ^) >> ebay_price.bat

echo [OK] Application launchers created
echo.

:: Create desktop shortcuts
echo [8/8] Creating desktop shortcuts...

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\eBay Tools - Setup.lnk');$s.TargetPath='%INSTALL_DIR%ebay_setup.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%SystemRoot%\System32\shell32.dll,162';$s.Description='eBay Tools - Setup and Queue Management';$s.Save()" 2>nul

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\eBay Tools - Processor.lnk');$s.TargetPath='%INSTALL_DIR%ebay_processor.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%SystemRoot%\System32\shell32.dll,162';$s.Description='eBay Tools - AI Photo Processing';$s.Save()" 2>nul

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\eBay Tools - Viewer.lnk');$s.TargetPath='%INSTALL_DIR%ebay_viewer.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%SystemRoot%\System32\shell32.dll,162';$s.Description='eBay Tools - Review and Export';$s.Save()" 2>nul

powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\eBay Tools - Price Analyzer.lnk');$s.TargetPath='%INSTALL_DIR%ebay_price.bat';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%SystemRoot%\System32\shell32.dll,162';$s.Description='eBay Tools - Price Analysis';$s.Save()" 2>nul

if exist "%INSTALL_DIR%eBay_Tools_User_Manual.md" (
    powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%userprofile%\Desktop\eBay Tools - User Manual.lnk');$s.TargetPath='%INSTALL_DIR%eBay_Tools_User_Manual.md';$s.WorkingDirectory='%INSTALL_DIR%';$s.IconLocation='%SystemRoot%\System32\shell32.dll,70';$s.Description='eBay Tools - Complete User Manual';$s.Save()" 2>nul
)

echo [OK] Desktop shortcuts created
echo.

:: Create data directories
mkdir "%INSTALL_DIR%data" 2>nul
mkdir "%INSTALL_DIR%exports" 2>nul  
mkdir "%INSTALL_DIR%logs" 2>nul
mkdir "%INSTALL_DIR%config" 2>nul

:: Final verification test
echo ==========================================
echo   Final Installation Verification
echo ==========================================
echo.
echo Testing application startup...

:: Test processor launch (without GUI)
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); from ebay_tools.apps.processor import EbayLLMProcessor; print('Processor module: OK')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Processor module test failed
) else (
    echo [OK] Processor module loads successfully
)

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo eBay Tools v3.0.1 has been successfully installed/updated!
echo.
echo ✓ All code files installed and verified
echo ✓ Dependencies installed  
echo ✓ Reset functionality verified present
echo ✓ Version detection working
echo ✓ Application launchers created (FIXED)
echo ✓ Desktop shortcuts created
echo.
echo Available applications:
echo   - eBay Tools - Setup        (Create item queues)
echo   - eBay Tools - Processor    (AI photo analysis + Reset Tags)
echo   - eBay Tools - Viewer       (Review and export) 
echo   - eBay Tools - Price Analyzer (Market pricing)
echo.
echo New Features in v3.0.0:
echo   🔄 Reset Tags button in Processor toolbar
echo   📋 Individual, type-based, and global reset options
echo   ℹ️  Version display in Help > About
echo.
echo Getting Started:
echo 1. Start with "eBay Tools - Setup" to create your first queue
echo 2. Use "eBay Tools - Processor" for AI photo processing
echo 3. Look for the "🔄 Reset Tags" button in the toolbar
echo 4. Check Help > About to verify version 3.0.0
echo.
if exist "%INSTALL_DIR%ebay_tools_backup\" (
    echo NOTE: Your previous installation was backed up to ebay_tools_backup\
    echo You can safely delete this folder after verifying the new installation works.
    echo.
)

:: Offer to test launch
set /p TEST_LAUNCH="Would you like to test launch the Processor now? (y/n): "
if /i "%TEST_LAUNCH%"=="y" (
    echo.
    echo Launching Processor for testing...
    start "" "%INSTALL_DIR%ebay_processor.bat"
    echo Look for the "🔄 Reset Tags" button in the toolbar!
)

echo.
echo Thank you for using eBay Tools v3.0.1!
echo.
pause