@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Собираю приложение в один exe-файл...
uv sync
uv run pyinstaller --onefile --name DeepSeekChat main.py

echo.
echo Готово. Файл будет здесь:
echo dist\DeepSeekChat.exe
pause
