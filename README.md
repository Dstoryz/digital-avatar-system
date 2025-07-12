# 🤖 Цифровой аватар с клонированием голоса и ИИ-общением

Интерактивный цифровой аватар с возможностью анимации лица, клонирования голоса и общения с использованием искусственного интеллекта.

## ✨ Возможности

- 🎭 **Анимация лица** - реалистичная анимация по фотографии с синхронизацией губ
- 🎤 **Клонирование голоса** - создание уникального голоса на основе аудиосэмплов
- 🧠 **ИИ-общение** - интеллектуальные ответы с учетом контекста и личности
- 🎯 **Распознавание речи** - преобразование речи в текст в реальном времени
- 🌐 **Веб-интерфейс** - современный React интерфейс с WebRTC
- ⚡ **Реальное время** - задержка 3-5 секунд для полного цикла обработки

## 🏗️ Архитектура

```
Frontend (React) ↔ Backend (FastAPI) ↔ AI Pipeline (GPU)
     ↓                    ↓                    ↓
  Веб-камера         WebSocket           CUDA Inference
  Микрофон           Redis Cache         Model Loading
  Аудио плеер        File Storage        GPU Memory Mgmt
```

## 🛠️ Технологический стек

### Backend (Python)
- **FastAPI** - веб-сервер с WebSocket поддержкой
- **SadTalker** - анимация лица и синхронизация губ
- **Wav2Lip** - точная синхронизация губ (опционально)
- **Coqui TTS** - клонирование голоса
- **Whisper** - распознавание речи
- **Ollama + Llama 3.2 8B** - генерация ответов
- **Real-ESRGAN** - улучшение качества видео
- **Redis** - кеширование результатов
- **SQLite** - локальная база данных

### Frontend (React)
- **React 18** с TypeScript
- **WebRTC** - работа с камерой и микрофоном
- **Socket.io** - реальное время
- **Tailwind CSS** - стилизация
- **Framer Motion** - анимации

## 📋 Системные требования

### Минимальные требования
- **GPU**: RTX 3060 12GB или аналогичный
- **CPU**: 8+ ядер
- **RAM**: 16GB (рекомендуется 32GB)
- **Storage**: 50GB свободного места
- **OS**: Linux (Ubuntu 20.04+)

### Программное обеспечение
- **Python**: 3.10+
- **CUDA**: 11.8+
- **Node.js**: 18+
- **Redis**: для кеширования
- **FFmpeg**: для обработки медиа

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/digital-avatar-system.git
cd digital-avatar-system
```

### 2. Настройка окружения
```bash
# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r backend/requirements.txt

# Установка Node.js зависимостей
cd frontend
npm install
cd ..
```

### 3. Настройка AI моделей
```bash
# Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:8b

# Скачивание SadTalker моделей
cd backend/ai_pipeline/face_animation
git clone https://github.com/OpenTalker/SadTalker.git
# Следуйте инструкциям в INSTALLATION_GUIDE.md
```

### 4. Запуск системы
```bash
# Запуск Redis
sudo systemctl start redis-server

# Запуск backend
cd backend
uvicorn app.main:app --reload

# Запуск frontend (в новом терминале)
cd frontend
npm run dev
```

## 📖 Документация

- [📋 Техническое задание](TECHNICAL_SPECIFICATION.md)
- [🏗️ Архитектура системы](ARCHITECTURE_DIAGRAM.md)
- [🔧 Руководство по установке](INSTALLATION_GUIDE.md)
- [📝 TODO-лист](TODO.md)
- [💬 Лог обсуждения проекта](CONVERSATION_LOG.md)

## 🎯 Использование

### Подготовка данных
1. **Фото девочки**: качественное фото 512x512, хорошее освещение
2. **Аудиосэмплы**: 5-10 минут чистых записей голоса (16kHz, WAV)

### Настройка персонажа
1. Загрузите фото и аудиосэмплы через веб-интерфейс
2. Настройте личность персонажа (имя, возраст, интересы)
3. Обучите модель клонирования голоса
4. Протестируйте систему

### Общение с аватаром
1. Откройте веб-интерфейс в браузере
2. Разрешите доступ к микрофону
3. Говорите или пишите сообщения
4. Наблюдайте анимированный ответ

## 🔧 Разработка

### Структура проекта
```
digital-avatar-system/
├── backend/              # FastAPI сервер
│   ├── app/             # Основное приложение
│   ├── ai_pipeline/     # AI модели и обработка
│   └── requirements.txt # Python зависимости
├── frontend/            # React приложение
│   ├── src/            # Исходный код
│   └── package.json    # Node.js зависимости
├── data/               # Медиафайлы и кеш
├── scripts/            # Утилиты и скрипты
└── docs/              # Документация
```

### Использование Cursor IDE
Проект настроен для эффективной разработки с Cursor IDE:
- [🎯 Настройка Cursor](CURSOR_SETUP.md)
- [📝 Готовые промпты](CURSOR_PROMPTS.md)
- [⚡ Быстрый старт](QUICKSTART.md)

## 📊 Производительность

### Ожидаемые характеристики
- **Общая задержка**: 3-5 секунд
- **Качество видео**: 512x512, 25 FPS
- **Качество аудио**: 16kHz, 16-bit
- **Потребление GPU**: ~8-10GB VRAM

### Распределение ресурсов
| Компонент | VRAM | Время выполнения |
|-----------|------|------------------|
| Whisper | 1GB | 0.5-1 сек |
| Llama 3.2 8B | 5GB | 1-3 сек |
| Coqui TTS | 2GB | 1-2 сек |
| SadTalker | 3GB | 2-3 сек |
| Real-ESRGAN | 1GB | 0.5 сек |

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🙏 Благодарности

- [SadTalker](https://github.com/OpenTalker/SadTalker) - анимация лица
- [Coqui TTS](https://github.com/coqui-ai/TTS) - синтез речи
- [Whisper](https://github.com/openai/whisper) - распознавание речи
- [Ollama](https://ollama.ai/) - локальные LLM модели

## 📞 Поддержка

Если у вас есть вопросы или проблемы:
- Создайте [Issue](https://github.com/your-username/digital-avatar-system/issues)
- Обратитесь к [документации](docs/)
- Проверьте [FAQ](docs/FAQ.md)

---

**Создайте свой собственный цифровой аватар! 🚀** 