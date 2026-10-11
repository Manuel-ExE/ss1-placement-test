@echo off
title Building SS1 Placement Test EXE
echo ============================================
echo  Building Windows EXE for
echo  Lagos State Senior Model College Ojo
echo  SS1 Placement Test
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo Installing required packages...
pip install customtkinter pyinstaller --quiet

echo.
echo Building the executable... This may take 1-3 minutes.
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "SS1_Placement_Test" ^
    --add-data "database.py;." ^
    --hidden-import=customtkinter ^
    --hidden-import=tkinter ^
    --collect-all customtkinter ^
    app.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  SUCCESS!
echo ============================================
echo.
echo Your EXE is ready at:
echo   dist\SS1_Placement_Test.exe
echo.
echo You can copy this file to any Windows computer.
echo No Python installation is needed to run it.
echo.
pause
