@echo off
title 🎣 WoW Fishing Bot

:: ─── Verifica se está rodando como Administrador ───────────────────────────
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo.
    echo  Elevando privilegios para Administrador...
    echo.
    :: Re-executa este mesmo .bat como Administrador
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: ─── Muda para a pasta do script ────────────────────────────────────────────
cd /d "%~dp0"

:: ─── Cabeçalho ───────────────────────────────────────────────────────────────
cls
echo.
echo  ==================================================
echo        WoW Fishing Bot - Iniciando...
echo  ==================================================
echo.
echo  Pasta: %~dp0
echo.

:: ─── Verifica se Python está instalado ──────────────────────────────────────
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    echo  [ERRO] Python nao encontrado! Instale em: https://python.org
    pause
    exit /b 1
)

:: ─── Instala dependencias automaticamente se necessario ─────────────────────
echo  Verificando dependencias...
pip install -r requirements.txt -q
echo  Dependencias OK!
echo.

:: ─── Inicia o bot ───────────────────────────────────────────────────────────
echo  Iniciando bot... (F8 para parar)
echo  ==================================================
echo.
python wow_fisher.py

:: ─── Aguarda ao terminar ─────────────────────────────────────────────────────
echo.
echo  ==================================================
echo  Bot encerrado. Pressione qualquer tecla para fechar.
echo  ==================================================
pause >nul
