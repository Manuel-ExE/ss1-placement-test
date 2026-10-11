@echo off
setlocal
cd /d "%~dp0"
title Build SS1 Placement Test Windows Installer
echo Building SS1 Placement Test Windows installer...
where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js and npm are required. Install Node.js 20 or newer.
  pause
  exit /b 1
)
call npm ci
if errorlevel 1 goto :failed
call npm test
if errorlevel 1 goto :failed
call npm run dist
if errorlevel 1 goto :failed
echo.
echo Installer created at: dist\SS1_Placement_Test_Setup.exe
pause
exit /b 0
:failed
echo.
echo BUILD FAILED. Review the error above.
pause
exit /b 1
