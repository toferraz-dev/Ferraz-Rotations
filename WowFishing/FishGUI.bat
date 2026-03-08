@echo off
title 🎣 WoW Fishing Bot GUI

:: Verifica Se esta rodando como Administrador
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo  Elevando privilegios para Administrador...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Muda para a pasta do script
cd /d "%~dp0"

echo  Instalando e verificando dependencias...
pip install -r requirements.txt -q

echo  Abrindo Bot GUI...
start pythonw wow_fisher_gui.py
