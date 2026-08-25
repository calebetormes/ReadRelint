@echo off
title Iniciar Painel ReadRelint
cd /d "%~dp0"

echo Iniciando o Painel de Controle Integrado e Servicos...
start "" ".venv\Scripts\pythonw.exe" painel.py --autostart
exit

