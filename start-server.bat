@echo off
echo ========================================
echo ROC Analytics Dashboard - Local Server
echo ========================================
echo.
echo Запуск локального веб-сервера...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Используется Python для запуска сервера...
    echo.
    echo Откройте в браузере: http://localhost:8000/index.html
    echo.
    echo Для остановки нажмите Ctrl+C
    echo.
    python -m http.server 8000
) else (
    echo Python не найден. Проверяем Node.js...
    node --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Используется Node.js для запуска сервера...
        echo.
        echo Откройте в браузере: http://localhost:8000/index.html
        echo.
        echo Для остановки нажмите Ctrl+C
        echo.
        npx http-server -p 8000
    ) else (
        echo.
        echo ОШИБКА: Не найден Python или Node.js!
        echo.
        echo Установите один из них:
        echo - Python: https://www.python.org/downloads/
        echo - Node.js: https://nodejs.org/
        echo.
        pause
    )
)

