#!/bin/bash

# Скрипт настройки окружения для проекта "Цифровой аватар"
# Автор: Авабот
# Версия: 1.0.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка операционной системы
check_os() {
    print_info "Проверка операционной системы..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Обнаружена Linux система"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Обнаружена macOS система"
    else
        print_error "Неподдерживаемая операционная система: $OSTYPE"
        exit 1
    fi
}

# Проверка и установка Python
setup_python() {
    print_info "Проверка Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python найден: $PYTHON_VERSION"
        
        # Проверка версии
        if [[ $(echo "$PYTHON_VERSION" | cut -d'.' -f1,2) < "3.10" ]]; then
            print_error "Требуется Python 3.10 или выше. Текущая версия: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python3 не найден. Установите Python 3.10+"
        exit 1
    fi
}

# Проверка и установка Node.js
setup_nodejs() {
    print_info "Проверка Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js найден: $NODE_VERSION"
        
        # Проверка версии
        if [[ $(echo "$NODE_VERSION" | cut -d'.' -f1) < "18" ]]; then
            print_error "Требуется Node.js 18 или выше. Текущая версия: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js не найден. Установите Node.js 18+"
        exit 1
    fi
}

# Проверка CUDA
check_cuda() {
    print_info "Проверка CUDA..."
    
    if command -v nvidia-smi &> /dev/null; then
        CUDA_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -1)
        print_success "CUDA найден: $CUDA_VERSION"
        
        # Проверка GPU памяти
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        print_info "GPU память: ${GPU_MEMORY}MB"
        
        if [[ $GPU_MEMORY -lt 8000 ]]; then
            print_warning "Рекомендуется GPU с памятью 8GB+. Текущая память: ${GPU_MEMORY}MB"
        fi
    else
        print_warning "CUDA не найден. Система будет работать на CPU (медленно)"
    fi
}

# Установка системных зависимостей
install_system_deps() {
    print_info "Установка системных зависимостей..."
    
    if [[ "$OS" == "linux" ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                python3-dev \
                python3-pip \
                python3-venv \
                ffmpeg \
                redis-server \
                git \
                curl \
                wget
        # CentOS/RHEL
        elif command -v yum &> /dev/null; then
            sudo yum update -y
            sudo yum install -y \
                gcc \
                gcc-c++ \
                python3-devel \
                python3-pip \
                ffmpeg \
                redis \
                git \
                curl \
                wget
        else
            print_error "Неподдерживаемый дистрибутив Linux"
            exit 1
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew update
            brew install \
                python@3.10 \
                node@18 \
                ffmpeg \
                redis \
                git
        else
            print_error "Homebrew не найден. Установите Homebrew для macOS"
            exit 1
        fi
    fi
}

# Создание виртуального окружения Python
setup_python_env() {
    print_info "Создание виртуального окружения Python..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        print_success "Виртуальное окружение создано"
    else
        print_info "Виртуальное окружение уже существует"
    fi
    
    # Активация окружения
    source venv/bin/activate
    
    # Обновление pip
    pip install --upgrade pip
    
    # Установка зависимостей
    print_info "Установка Python зависимостей..."
    pip install -r backend/requirements.txt
    
    print_success "Python зависимости установлены"
}

# Установка Node.js зависимостей
setup_nodejs_deps() {
    print_info "Установка Node.js зависимостей..."
    
    cd frontend
    
    if [[ ! -d "node_modules" ]]; then
        npm install
        print_success "Node.js зависимости установлены"
    else
        print_info "Node.js зависимости уже установлены"
    fi
    
    cd ..
}

# Настройка Redis
setup_redis() {
    print_info "Настройка Redis..."
    
    if command -v redis-server &> /dev/null; then
        # Проверка статуса Redis
        if pgrep redis-server > /dev/null; then
            print_success "Redis уже запущен"
        else
            print_info "Запуск Redis..."
            sudo systemctl start redis-server || redis-server --daemonize yes
            print_success "Redis запущен"
        fi
        
        # Проверка подключения
        if redis-cli ping > /dev/null 2>&1; then
            print_success "Redis подключение работает"
        else
            print_error "Ошибка подключения к Redis"
            exit 1
        fi
    else
        print_error "Redis не установлен"
        exit 1
    fi
}

# Создание конфигурационных файлов
create_configs() {
    print_info "Создание конфигурационных файлов..."
    
    # Создание .env файла
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Конфигурация окружения
ENVIRONMENT=development
DEBUG=true

# Сервер
HOST=0.0.0.0
PORT=8000

# База данных
DATABASE_URL=sqlite:///./data/avatar.db

# Redis
REDIS_URL=redis://localhost:6379

# AI модели
MODELS_PATH=./data/models
CACHE_PATH=./data/cache

# GPU
USE_GPU=true
CUDA_VISIBLE_DEVICES=0

# Безопасность
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]

# Логирование
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF
        print_success "Файл .env создан"
    else
        print_info "Файл .env уже существует"
    fi
    
    # Создание конфигурации для frontend
    if [[ ! -f "frontend/.env" ]]; then
        cat > frontend/.env << EOF
# Frontend конфигурация
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Цифровой Аватар
EOF
        print_success "Файл frontend/.env создан"
    else
        print_info "Файл frontend/.env уже существует"
    fi
}

# Проверка установки
verify_installation() {
    print_info "Проверка установки..."
    
    # Проверка Python
    source venv/bin/activate
    python -c "import torch; print(f'PyTorch: {torch.__version__}')"
    python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
    
    # Проверка Node.js
    cd frontend
    npm run type-check
    cd ..
    
    print_success "Все проверки пройдены успешно!"
}

# Основная функция
main() {
    print_info "Настройка окружения для проекта 'Цифровой аватар'"
    print_info "Автор: Авабот"
    echo
    
    check_os
    setup_python
    setup_nodejs
    check_cuda
    install_system_deps
    setup_python_env
    setup_nodejs_deps
    setup_redis
    create_configs
    verify_installation
    
    echo
    print_success "Настройка окружения завершена успешно!"
    print_info "Следующие шаги:"
    print_info "1. Активируйте виртуальное окружение: source venv/bin/activate"
    print_info "2. Запустите backend: cd backend && uvicorn app.main:app --reload"
    print_info "3. Запустите frontend: cd frontend && npm run dev"
    print_info "4. Откройте браузер: http://localhost:3000"
}

# Запуск скрипта
main "$@" 