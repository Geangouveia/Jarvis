@echo off
title J.A.R.V.I.S. // Stark Industries Operating System
color 0b

echo ========================================================
echo       J.A.R.V.I.S. - PROTOCOLO STARK INICIANDO
echo ========================================================
echo.
echo Verificando dependencias...
python -m pip install -r requirements.txt --quiet

echo.
echo Iniciando Servidor e Interface HUD Holografica...
start http://127.0.0.1:8000
python server.py

pause
