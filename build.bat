@echo off
REM Build script for Path of Python
REM This script builds the game into a standalone Windows executable

echo ========================================
echo Path of Python - Build Script
echo ========================================
echo.

REM Remove obsolete pathlib backport if it exists (causes PyInstaller conflicts)
python -c "import pathlib; import sys; sys.exit(0 if pathlib.__file__.endswith('site-packages\\pathlib.py') else 1)" 2>nul
if not errorlevel 1 (
    echo Removing obsolete pathlib backport...
    pip uninstall pathlib -y
    echo.
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo Cleaning previous build...
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    if exist "dist" (
        echo WARNING: Could not delete dist folder ^(file locked^). Renaming instead...
        move dist dist_old_%RANDOM% 2>nul
    )
)
if exist "build" rmdir /s /q "build" 2>nul
echo.

echo Building executable...
echo This may take a few minutes...
echo.
pyinstaller path_of_python.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo Build FAILED!
    echo Check the error messages above.
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build SUCCESSFUL!
echo ========================================
echo.
echo Your executable is located at:
echo dist\PathOfPython.exe
echo.
echo File size:
for %%A in ("dist\PathOfPython.exe") do echo %%~zA bytes
echo.
pause
