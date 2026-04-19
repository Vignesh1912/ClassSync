@echo off
echo Starting ClassSync App...
start "ClassSync Server" cmd /k ".\venv\Scripts\activate && python run.py"

echo Starting Tunnel...
start "ClassSync Tunnel" cmd /k "npx untun@latest tunnel http://127.0.0.1:5000"

echo.
echo ========================================================
echo IMPORTANT: In the new Tunnel window, if it asks to accept
echo the Cloudflare license, just type 'Y' and hit Enter!
echo.
echo Please use the blazing fast "trycloudflare.com" link 
echo that generates inside that window.
echo ========================================================
echo.
echo Note: Keep the two console windows open to keep the website online!
pause
