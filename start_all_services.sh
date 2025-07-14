#!/bin/bash

# Скрипт для запуска всех сервисов системы цифрового аватара
# Автор: Авабот
# Версия: 1.0.0

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    log_info "Проверка зависимостей..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 не установлен"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js не установлен"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm не установлен"
        exit 1
    fi
    
    log_success "Все зависимости установлены"
}

# Проверка виртуальных окружений
check_environments() {
    log_info "Проверка виртуальных окружений..."
    
    if [ ! -d "ai_env" ]; then
        log_error "Окружение ai_env не найдено"
        exit 1
    fi
    
    if [ ! -d "sadtalker_env310" ]; then
        log_error "Окружение sadtalker_env310 не найдено"
        exit 1
    fi
    
    log_success "Виртуальные окружения найдены"
}

# Функция для ожидания готовности сервиса
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "Ожидание готовности $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$service_name готов к работе"
            return 0
        fi
        
        log_info "Попытка $attempt/$max_attempts - $service_name еще не готов..."
        sleep 2
        ((attempt++))
    done
    
    log_error "$service_name не запустился за отведенное время"
    return 1
}

# Запуск Backend API
start_backend() {
    log_info "Запуск Backend API (порт 8000)..."
    
    cd backend
    source ../ai_env/bin/activate
    
    # Запуск в фоне с перенаправлением вывода
    nohup python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    cd ..
    
    # Ожидание готовности
    if wait_for_service "http://localhost:8000/health" "Backend API"; then
        log_success "Backend API запущен (PID: $BACKEND_PID)"
    else
        log_error "Ошибка запуска Backend API"
        exit 1
    fi
}

# Запуск HierSpeech_TTS
start_hier_tts() {
    log_info "Запуск HierSpeech_TTS (порт 8001)..."
    
    cd HierSpeech_TTS
    source ../ai_env/bin/activate
    
    # Запуск в фоне с перенаправлением вывода
    nohup python hier_api_server.py > ../logs/hier_tts.log 2>&1 &
    HIER_TTS_PID=$!
    echo $HIER_TTS_PID > ../logs/hier_tts.pid
    
    cd ..
    
    # Ожидание готовности
    if wait_for_service "http://localhost:8001/health" "HierSpeech_TTS"; then
        log_success "HierSpeech_TTS запущен (PID: $HIER_TTS_PID)"
    else
        log_error "Ошибка запуска HierSpeech_TTS"
        exit 1
    fi
}

# Запуск SadTalker
start_sadtalker() {
    log_info "Запуск SadTalker (порт 8002)..."
    
    cd SadTalker
    source ../sadtalker_env310/bin/activate
    
    # Запуск в фоне с перенаправлением вывода
    nohup python sadtalker_api_server.py > ../logs/sadtalker.log 2>&1 &
    SADTALKER_PID=$!
    echo $SADTALKER_PID > ../logs/sadtalker.pid
    
    cd ..
    
    # Ожидание готовности
    if wait_for_service "http://localhost:8002/health" "SadTalker"; then
        log_success "SadTalker запущен (PID: $SADTALKER_PID)"
    else
        log_error "Ошибка запуска SadTalker"
        exit 1
    fi
}

# Запуск Frontend
start_frontend() {
    log_info "Запуск Frontend (порт 3000)..."
    
    cd frontend
    
    # Запуск в фоне с перенаправлением вывода
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
    
    # Ожидание готовности
    if wait_for_service "http://localhost:3000" "Frontend"; then
        log_success "Frontend запущен (PID: $FRONTEND_PID)"
    else
        log_error "Ошибка запуска Frontend"
        exit 1
    fi
}

# Проверка статуса всех сервисов
check_all_services() {
    log_info "Проверка статуса всех сервисов..."
    
    local services=(
        "Backend API:http://localhost:8000/health"
        "HierSpeech_TTS:http://localhost:8001/health"
        "SadTalker:http://localhost:8002/health"
        "Frontend:http://localhost:3000"
    )
    
    local all_ok=true
    
    for service in "${services[@]}"; do
        IFS=':' read -r name url <<< "$service"
        
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$name работает"
        else
            log_error "$name не отвечает"
            all_ok=false
        fi
    done
    
    if [ "$all_ok" = true ]; then
        log_success "Все сервисы работают корректно!"
        echo ""
        echo "🌐 Доступные URL:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:8000"
        echo "   HierSpeech_TTS: http://localhost:8001"
        echo "   SadTalker: http://localhost:8002"
        echo ""
        echo "📋 Логи сервисов:"
        echo "   Backend: logs/backend.log"
        echo "   HierSpeech_TTS: logs/hier_tts.log"
        echo "   SadTalker: logs/sadtalker.log"
        echo "   Frontend: logs/frontend.log"
        echo ""
        echo "🛑 Для остановки всех сервисов выполните: ./stop_all_services.sh"
    else
        log_error "Некоторые сервисы не работают"
        exit 1
    fi
}

# Создание директории для логов
create_logs_directory() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
        log_info "Создана директория logs"
    fi
}

# Основная функция
main() {
    echo "🚀 Запуск системы цифрового аватара"
    echo "=================================="
    echo ""
    
    # Проверки
    check_dependencies
    check_environments
    create_logs_directory
    
    # Остановка существующих процессов
    log_info "Остановка существующих процессов..."
    ./stop_all_services.sh 2>/dev/null || true
    
    # Запуск сервисов
    start_backend
    start_hier_tts
    start_sadtalker
    start_frontend
    
    # Финальная проверка
    check_all_services
    
    log_success "Система цифрового аватара успешно запущена!"
}

# Обработка сигналов
trap 'log_info "Получен сигнал остановки. Завершение работы..."; exit 0' SIGINT SIGTERM

# Запуск основной функции
main "$@" 