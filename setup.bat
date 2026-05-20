@echo off
echo ========================================
echo  Seance 👻 — Ghost Chat Setup (Windows)
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python is installed.
    pause
    exit /b 1
)
echo.
echo ✅ Setup complete! 
echo.
echo To start the server:
echo   python seance.py serve
echo.
echo To send a message from terminal:
echo   python seance.py send "Hello!" --from desktop
echo.
echo Then open http://localhost:5555 in your browser!
echo.
pause
