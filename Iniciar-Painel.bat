@echo off
title Iniciar Painel ReadRelint
cd /d "%~dp0"

echo Iniciando Backend (FastAPI)...
start "FastAPI Backend" cmd /c ".venv\Scripts\python.exe -m uvicorn backend.api.app:app --reload"

echo Iniciando Frontend (SvelteKit)...
cd frontend
start "SvelteKit Frontend" cmd /c "npm run dev -- --open"

echo.
echo Tudo iniciado! 
echo Se o navegador nao abrir automaticamente, acesse: http://localhost:5173
pause
