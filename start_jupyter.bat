@echo off
rem Start JupyterLab for this project. Double-click this file.
rem The window that opens IS the server - leave it open, close it to stop.
cd /d "%~dp0"
echo.
echo   Starting JupyterLab in:  %cd%
echo   The browser opens in a few seconds.
echo.
echo   KEEP THIS WINDOW OPEN while you work.
echo   To stop: close this window, or press Ctrl+C twice.
echo.
start "" /b cmd /c "timeout /t 5 >nul & start "" "http://localhost:8888/lab?token=bearing""
python -m jupyter lab --no-browser --IdentityProvider.token=bearing
echo.
echo   Server stopped.
pause
