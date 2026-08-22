@echo off
title Iniciar Painel ReadRelint
cd /d "%~dp0"

echo Iniciando o Painel de Controle Integrado...
start "" ".venv\Scripts\pythonw.exe" painel.py
exit
