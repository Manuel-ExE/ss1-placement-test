@echo off
title Lagos State Senior Model College Ojo - SS1 Placement Test
echo Starting application...
python app.py
if errorlevel 1 (
    echo.
    echo Python not found or an error occurred.
    echo Make sure Python is installed and added to PATH.
    echo Then run:  pip install -r requirements.txt
    pause
)
