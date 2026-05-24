@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Собираю приложение в один exe-файл...
.venv\Scripts\python.exe -m PyInstaller --onefile --name DeepSeekChat main.py

echo.
echo Готово. Файл будет здесь:
echo dist\DeepSeekChat.exe
pause
