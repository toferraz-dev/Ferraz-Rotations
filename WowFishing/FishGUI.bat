@echo off
title 🎣 Ferraz Fishing WoW GUI

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% NEQ 0 (
    powershell -nop -c "Add-Type -AssemblyName PresentationFramework; $res = [System.Windows.MessageBox]::Show('Python was not found on your computer.' + [Environment]::NewLine + 'It is required to run the bot.' + [Environment]::NewLine + [Environment]::NewLine + 'Would you like to download Python now? (Remember to check ''Add Python to PATH'' during installation)', 'Ferraz Fishing WoW - Warning', 'YesNo', 'Warning'); if ($res -eq 'Yes') { Start-Process 'https://www.python.org/downloads/windows/' }"
    exit /b 1
)

:: Check if running as Administrator
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo  Elevating privileges to Administrator...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Change to the script folder
cd /d "%~dp0"

echo  Installing and checking dependencies...
pip install -r requirements.txt -q

echo  Opening Bot GUI...
start pythonw wow_fisher_gui.py
