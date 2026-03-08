@echo off
title 🎣 WoW Fishing Bot GUI

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo Feche esta janela, instale o Python usando o atalho "Baixar_Python" e tente novamente!
    echo.
    echo Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao!
    pause
    start https://www.python.org/downloads/windows/
    exit /b 1
)

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
