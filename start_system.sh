#!/bin/bash

# Скрипт запуска системы цифрового аватара
# Backend: порт 8000, Frontend: порт 3000

echo "🚀 Запуск системы цифрового аватара"
echo "=================================="

# Остановка существующих процессов
echo "🛑 Остановка существующих процессов..."
pkill -f "uvicorn.*8000" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Запуск backend
echo "🔧 Запуск backend (порт 8000)..."
source ai_env/bin/activate
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Ожидание запуска backend
sleep 3

# Проверка backend
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend запущен на http://127.0.0.1:8000"
else
    echo "❌ Ошибка запуска backend"
    exit 1
fi

# Запуск frontend
echo "🎨 Запуск frontend (порт 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Ожидание запуска frontend
sleep 5

# Проверка frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend запущен на http://localhost:3000"
else
    echo "❌ Ошибка запуска frontend"
    exit 1
fi

echo ""
echo "🎉 Система запущена!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://127.0.0.1:8000"
echo "📚 API docs: http://127.0.0.1:8000/docs"
echo ""
echo "Для остановки нажмите Ctrl+C"

# Ожидание сигнала завершения
trap "echo '🛑 Остановка системы...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait 