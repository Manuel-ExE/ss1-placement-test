@echo off
setlocal
cd /d "%~dp0"
title SS1 Placement Test - Development Launcher
where npm >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js and npm are required. Install Node.js 20 or newer.
  pause
  exit /b 1
)
if not exist node_modules\electron (
  echo Installing app dependencies...
  call npm ci
  if errorlevel 1 goto :failed
)
call npm start
if errorlevel 1 goto :failed
exit /b 0
:failed
echo.
echo Application launch failed. Review the error above.
pause
exit /b 1
