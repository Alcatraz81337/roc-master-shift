#!/bin/bash

echo "========================================"
echo "ROC Analytics Dashboard - Local Server"
echo "========================================"
echo ""
echo "Запуск локального веб-сервера..."
echo ""

# Проверяем наличие Python
if command -v python3 &> /dev/null; then
    echo "Используется Python 3 для запуска сервера..."
    echo ""
    echo "Откройте в браузере: http://localhost:8000/index.html"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    echo ""
    python3 -m http.server 8000
elif command -v python &> /dev/null; then
    echo "Используется Python для запуска сервера..."
    echo ""
    echo "Откройте в браузере: http://localhost:8000/index.html"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    echo ""
    python -m SimpleHTTPServer 8000
elif command -v node &> /dev/null; then
    echo "Используется Node.js для запуска сервера..."
    echo ""
    echo "Откройте в браузере: http://localhost:8000/index.html"
    echo ""
    echo "Для остановки нажмите Ctrl+C"
    echo ""
    npx http-server -p 8000
else
    echo ""
    echo "ОШИБКА: Не найден Python или Node.js!"
    echo ""
    echo "Установите один из них:"
    echo "- Python: https://www.python.org/downloads/"
    echo "- Node.js: https://nodejs.org/"
    echo ""
    exit 1
fi

