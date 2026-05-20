@echo off
call conda activate strulovitzghost
cd /d "%~dp0"
echo.
echo  ========================================
echo   Seance 👻 — Ghost Chat
echo  ========================================
echo.
echo   Chat UI:  http://localhost:5555
echo   Stop:     Press Ctrl+C or close this window
echo  ========================================
echo.
python seance.py serve
pause
