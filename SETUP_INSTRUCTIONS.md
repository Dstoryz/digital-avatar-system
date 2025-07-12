# 🚀 Инструкции по настройке и запуску

## Быстрый старт

### 1. Автоматическая настройка (рекомендуется)

```bash
# Сделать скрипт исполняемым
chmod +x scripts/setup_environment.sh

# Запустить автоматическую настройку
./scripts/setup_environment.sh
```

### 2. Ручная настройка

#### Проверка системных требований

```bash
# Python 3.10+
python3 --version

# Node.js 18+
node --version

# CUDA (опционально)
nvidia-smi

# Redis
redis-cli ping
```

#### Установка зависимостей

```bash
# Python зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Node.js зависимости
cd frontend
npm install
cd ..
```

#### Настройка окружения

```bash
# Создание .env файлов
cp .env.example .env
cp frontend/.env.example frontend/.env

# Редактирование настроек
nano .env
nano frontend/.env
```

## Запуск приложения

### 1. Запуск backend

```bash
# Активация виртуального окружения
source venv/bin/activate

# Запуск FastAPI сервера
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Запуск frontend

```bash
# В новом терминале
cd frontend
npm run dev
```

### 3. Проверка работы

- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Структура проекта

```
digital-avatar-system/
├── backend/                 # FastAPI backend
│   ├── app/                # Основное приложение
│   │   ├── main.py         # Точка входа
│   │   ├── config.py       # Конфигурация
│   │   ├── routers/        # API роутеры
│   │   └── services/       # Бизнес-логика
│   ├── ai_pipeline/        # AI модели
│   │   ├── face_animation/ # SadTalker
│   │   ├── voice_cloning/  # Coqui TTS
│   │   ├── speech_recognition/ # Whisper
│   │   └── llm_integration/ # Ollama + Llama
│   └── tests/              # Тесты
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── hooks/          # Custom hooks
│   │   ├── utils/          # Утилиты
│   │   └── types/          # TypeScript типы
│   └── public/             # Статические файлы
├── data/                   # Данные и кеш
│   ├── audio/              # Аудиофайлы
│   ├── images/             # Изображения
│   ├── cache/              # Кеш
│   └── models/             # AI модели
├── scripts/                # Скрипты
└── docs/                   # Документация
```

## Конфигурация

### Backend (.env)

```env
# Основные настройки
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
```

### Frontend (.env)

```env
# Frontend конфигурация
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Цифровой Аватар
```

## Разработка

### Команды для разработки

```bash
# Backend
cd backend
uvicorn app.main:app --reload  # Автоперезагрузка
pytest                         # Запуск тестов
black .                        # Форматирование кода
flake8 .                       # Линтинг

# Frontend
cd frontend
npm run dev                    # Разработка
npm run build                  # Сборка
npm run test                   # Тесты
npm run lint                   # Линтинг
npm run format                 # Форматирование
```

### Отладка

```bash
# Логи backend
tail -f logs/backend.log

# Логи frontend
npm run dev  # Логи в консоли браузера

# Мониторинг GPU
watch -n 1 nvidia-smi

# Мониторинг Redis
redis-cli monitor
```

## Устранение неполадок

### Частые проблемы

1. **CUDA не найден**
   ```bash
   # Проверка установки CUDA
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Redis не запущен**
   ```bash
   # Запуск Redis
   sudo systemctl start redis-server
   # или
   redis-server --daemonize yes
   ```

3. **Порт занят**
   ```bash
   # Поиск процесса
   lsof -i :8000
   lsof -i :3000
   
   # Завершение процесса
   kill -9 <PID>
   ```

4. **Ошибки зависимостей**
   ```bash
   # Переустановка Python зависимостей
   pip uninstall -r backend/requirements.txt -y
   pip install -r backend/requirements.txt
   
   # Переустановка Node.js зависимостей
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Логи и отладка

```bash
# Включение debug режима
export DEBUG=true
export LOG_LEVEL=DEBUG

# Подробные логи
uvicorn app.main:app --reload --log-level debug
```

## Следующие шаги

После успешного запуска:

1. **Подготовка данных**
   - Загрузите фото девочки в `data/images/`
   - Загрузите аудиосэмплы в `data/audio/`

2. **Настройка AI моделей**
   - Следуйте инструкциям в `INSTALLATION_GUIDE.md`
   - Установите SadTalker, Coqui TTS, Whisper

3. **Тестирование**
   - Проверьте API endpoints
   - Протестируйте WebSocket соединения
   - Убедитесь в работе frontend

4. **Разработка**
   - Изучите TODO.md для понимания задач
   - Используйте Cursor IDE с настроенными правилами
   - Следуйте CONTRIBUTING.md для вклада в проект

## Поддержка

- **Документация**: `docs/`
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Автор**: Авабот

---

**Удачной разработки! 🚀** 