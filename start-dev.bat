@echo off
REM Script de démarrage du AI Service pour développement mobile
REM Lance le serveur accessible depuis le réseau local

echo 🚀 Démarrage du AI Service...
echo.
echo 📱 Ce serveur sera accessible depuis:
echo    - Web: http://127.0.0.1:8000
echo    - Mobile: http://[VOTRE_IP]:8000
echo.
echo 🔍 Pour trouver votre IP: ipconfig
echo.

cd /d "%~dp0"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
