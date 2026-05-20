@echo off
cd /d "%~dp0"
echo.
echo  ========================================
echo   Seance 👻 — Ghost Chat + Bridge
echo  ========================================
echo.
echo   Chat UI:     http://localhost:5555
echo   Bridge:      Forwarding to OpenCode port 4096
echo   Auto-submit: ON (triggers AI responses)
echo   Stop:        Press Ctrl+C or close this window
echo  ========================================
echo.
start "Seance Server" python seance.py serve
timeout /t 3 /nobreak >nul
python seance.py bridge --name laptop --opencode-port 4096 --auto-submit
pause
