#!/bin/bash

# Скрипт для остановки всех сервисов системы цифрового аватара
# Автор: Авабот
# Версия: 1.0.0

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

# Функция для остановки процесса по PID файлу
stop_service() {
    local service_name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log_info "Остановка $service_name (PID: $pid)..."
            
            # Сначала пытаемся остановить gracefully
            kill -TERM "$pid" 2>/dev/null
            
            # Ждем 5 секунд
            sleep 5
            
            # Проверяем, остановился ли процесс
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "$service_name не остановился gracefully, принудительная остановка..."
                kill -KILL "$pid" 2>/dev/null
                sleep 2
            fi
            
            # Финальная проверка
            if ps -p "$pid" > /dev/null 2>&1; then
                log_error "Не удалось остановить $service_name"
                return 1
            else
                log_success "$service_name остановлен"
                rm -f "$pid_file"
                return 0
            fi
        else
            log_warning "$service_name уже остановлен"
            rm -f "$pid_file"
            return 0
        fi
    else
        log_warning "PID файл для $service_name не найден"
        return 0
    fi
}

# Функция для остановки процессов по имени
stop_processes_by_name() {
    local process_name=$1
    local service_name=$2
    
    log_info "Поиск процессов $service_name..."
    
    # Находим все процессы с указанным именем
    local pids=$(pgrep -f "$process_name" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        log_info "Найдены процессы $service_name: $pids"
        
        for pid in $pids; do
            log_info "Остановка процесса $service_name (PID: $pid)..."
            
            # Сначала пытаемся остановить gracefully
            kill -TERM "$pid" 2>/dev/null
            
            # Ждем 3 секунды
            sleep 3
            
            # Проверяем, остановился ли процесс
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "Процесс $service_name не остановился gracefully, принудительная остановка..."
                kill -KILL "$pid" 2>/dev/null
                sleep 1
            fi
            
            # Финальная проверка
            if ps -p "$pid" > /dev/null 2>&1; then
                log_error "Не удалось остановить процесс $service_name (PID: $pid)"
            else
                log_success "Процесс $service_name (PID: $pid) остановлен"
            fi
        done
    else
        log_info "Процессы $service_name не найдены"
    fi
}

# Основная функция остановки
main() {
    echo "🛑 Остановка системы цифрового аватара"
    echo "====================================="
    echo ""
    
    # Остановка сервисов по PID файлам
    log_info "Остановка сервисов по PID файлам..."
    
    stop_service "Backend API" "logs/backend.pid"
    stop_service "HierSpeech_TTS" "logs/hier_tts.pid"
    stop_service "SadTalker" "logs/sadtalker.pid"
    stop_service "Frontend" "logs/frontend.pid"
    
    # Дополнительная остановка по именам процессов
    log_info "Дополнительная остановка процессов..."
    
    stop_processes_by_name "uvicorn.*app.main:app" "Backend API"
    stop_processes_by_name "hier_api_server.py" "HierSpeech_TTS"
    stop_processes_by_name "sadtalker_api_server.py" "SadTalker"
    stop_processes_by_name "vite.*dev" "Frontend"
    stop_processes_by_name "node.*dev" "Frontend"
    
    # Остановка процессов на портах
    log_info "Остановка процессов на портах..."
    
    local ports=(8000 8001 8002 3000)
    
    for port in "${ports[@]}"; do
        local pid=$(lsof -ti:$port 2>/dev/null || true)
        
        if [ -n "$pid" ]; then
            log_info "Остановка процесса на порту $port (PID: $pid)..."
            kill -TERM "$pid" 2>/dev/null
            sleep 2
            
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "Принудительная остановка процесса на порту $port..."
                kill -KILL "$pid" 2>/dev/null
            fi
        fi
    done
    
    # Очистка временных файлов
    log_info "Очистка временных файлов..."
    
    if [ -d "logs" ]; then
        rm -f logs/*.pid
        log_success "PID файлы удалены"
    fi
    
    # Финальная проверка
    log_info "Проверка оставшихся процессов..."
    
    local remaining_processes=0
    
    # Проверяем процессы на портах
    for port in "${ports[@]}"; do
        if lsof -i:$port > /dev/null 2>&1; then
            log_warning "Порт $port все еще занят"
            remaining_processes=$((remaining_processes + 1))
        fi
    done
    
    # Проверяем специфичные процессы
    if pgrep -f "uvicorn.*app.main:app" > /dev/null 2>&1; then
        log_warning "Backend API процессы все еще активны"
        remaining_processes=$((remaining_processes + 1))
    fi
    
    if pgrep -f "hier_api_server.py" > /dev/null 2>&1; then
        log_warning "HierSpeech_TTS процессы все еще активны"
        remaining_processes=$((remaining_processes + 1))
    fi
    
    if pgrep -f "sadtalker_api_server.py" > /dev/null 2>&1; then
        log_warning "SadTalker процессы все еще активны"
        remaining_processes=$((remaining_processes + 1))
    fi
    
    if pgrep -f "vite.*dev" > /dev/null 2>&1; then
        log_warning "Frontend процессы все еще активны"
        remaining_processes=$((remaining_processes + 1))
    fi
    
    if [ $remaining_processes -eq 0 ]; then
        log_success "Все сервисы успешно остановлены!"
    else
        log_warning "Некоторые процессы все еще активны. Возможно, потребуется ручная остановка."
    fi
    
    echo ""
    echo "📋 Для просмотра логов:"
    echo "   Backend: tail -f logs/backend.log"
    echo "   HierSpeech_TTS: tail -f logs/hier_tts.log"
    echo "   SadTalker: tail -f logs/sadtalker.log"
    echo "   Frontend: tail -f logs/frontend.log"
    echo ""
    echo "🚀 Для повторного запуска выполните: ./start_all_services.sh"
}

# Обработка сигналов
trap 'log_info "Получен сигнал остановки. Завершение работы..."; exit 0' SIGINT SIGTERM

# Запуск основной функции
main "$@" 