@echo off
title Desativar Inicializacao Automatica do J.A.R.V.I.S.
color 0c

set VBS_TARGET=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Jarvis_AutoStart.vbs

if exist "%VBS_TARGET%" (
    del "%VBS_TARGET%"
    echo [SUCESSO] Inicializacao automatica removida com sucesso.
) else (
    echo [INFO] O J.A.R.V.I.S. nao estava configurado na inicializacao.
)

pause
