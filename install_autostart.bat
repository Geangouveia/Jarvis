@echo off
title Configurar Inicializacao Automatica do J.A.R.V.I.S.
color 0a

echo ========================================================
echo   CONFIGURANDO J.A.R.V.I.S. PARA INICIAR COM O WINDOWS
echo ========================================================
echo.

set SCRIPT_DIR=%~dp0
set VBS_TARGET=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Jarvis_AutoStart.vbs

echo Criando script silencioso de inicializacao...
(
    echo Set WshShell = CreateObject^("WScript.Shell"^)
    echo WshShell.CurrentDirectory = "%SCRIPT_DIR%"
    echo WshShell.Run "python server.py", 0, False
    echo WScript.Sleep 2000
    echo WshShell.Run "cmd /c start http://127.0.0.1:8000", 0, False
) > "%VBS_TARGET%"

echo.
echo [SUCESSO] O J.A.R.V.I.S. agora sera iniciado automaticamente toda vez que voce ligar o PC!
echo Local do gatilho: %VBS_TARGET%
echo.
pause
