@echo off
title 🎣 Ferraz Fishing WoW GUI

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    powershell -nop -c "Add-Type -AssemblyName PresentationFramework; $res = [System.Windows.MessageBox]::Show('O Python não foi encontrado no seu computador.' + [Environment]::NewLine + 'Ele é obrigatório para rodar o bot.' + [Environment]::NewLine + [Environment]::NewLine + 'Deseja baixar o Python agora? (Lembre-se de marcar ''Add Python to PATH'' na instalacao)', 'Ferraz Fishing WoW - Aviso', 'YesNo', 'Warning'); if ($res -eq 'Yes') { Start-Process 'https://www.python.org/downloads/windows/' }"
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
