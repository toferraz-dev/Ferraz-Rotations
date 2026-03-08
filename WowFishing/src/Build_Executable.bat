@echo off
echo Installing PyInstaller...
python -m pip install pyinstaller -q

echo.
echo Building Ferraz Fishing Executable...
echo This might take a few minutes...
python -m PyInstaller --noconfirm --onefile --windowed --icon "icon.ico" --name "Ferraz Fishing" --add-data "icon.png;." --add-data "icon.ico;." --collect-all customtkinter "wow_fisher_gui.py"

echo.
echo Build complete! Your executable is located in the "dist" folder.
pause
