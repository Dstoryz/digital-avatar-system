# Руководство по настройке Cursor для проекта "Цифровой аватар"

## 🚀 Быстрая настройка

### 1. Создание папки .vscode
```bash
mkdir -p .vscode
cp cursor-settings.json .vscode/settings.json
```

### 2. Установка необходимых расширений
Откройте Cursor и установите следующие расширения:

**Для Python:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Python Docstring Generator (njpwerner.autodocstring)
- Black Formatter (ms-python.black-formatter)
- Flake8 (ms-python.flake8)
- Mypy Type Checker (ms-python.mypy-type-checker)

**Для TypeScript/React:**
- TypeScript Importer (pmneo.tsimporter)
- ES7+ React/Redux/React-Native snippets (dsznajder.es7-react-js-snippets)
- Auto Rename Tag (formulahendry.auto-rename-tag)
- Bracket Pair Colorizer (coenraads.bracket-pair-colorizer)
- Prettier - Code formatter (esbenp.prettier-vscode)

**Для общей разработки:**
- GitLens (eamodio.gitlens)
- Material Icon Theme (pkief.material-icon-theme)
- TODO Highlight (wayou.vscode-todo-highlight)
- Code Spell Checker (streetsidesoftware.code-spell-checker)
- Russian - Code Spell Checker (streetsidesoftware.code-spell-checker-russian)

**Для работы с AI/ML:**
- Jupyter (ms-toolsai.jupyter)
- YAML (redhat.vscode-yaml)
- Docker (ms-azuretools.vscode-docker)

---

## 🎯 Эффективное использование Cursor для проекта

### 1. Cursor Chat (Ctrl+L)

#### Основные команды для проекта:
```
@codebase Создай класс для управления контекстом нейронной личности с поддержкой эмоций, памяти и персонализации

@codebase Как оптимизировать использование GPU памяти для одновременной работы SadTalker, Whisper и Llama на RTX 3060 12GB?

@codebase Реализуй FastAPI endpoint для обработки аудио с WebSocket поддержкой для реального времени

@codebase Создай React компонент для отображения анимированного аватара с поддержкой эмоций и состояний загрузки
```

#### Специфичные для AI задачи:
```
@codebase Интегрируй Coqui TTS с fine-tuning для клонирования голоса девочки

@codebase Реализуй пайплайн SadTalker + Wav2Lip с оптимизацией GPU памяти

@codebase Создай систему кеширования для частых AI операций с Redis

@codebase Добавь мониторинг GPU ресурсов и автоматическую очистку памяти
```

### 2. Cursor Composer (Ctrl+I)

#### Создание больших модулей:
```
Создай полный модуль для анимации лица:
- Класс FaceAnimator с методами для SadTalker и Wav2Lip
- Предобработка изображений с Real-ESRGAN
- Обработка ошибок и логирование
- Оптимизация для GPU RTX 3060
- Unit тесты для всех методов
- Типизация TypeScript для API
```

#### Создание React компонентов:
```
Создай компонент AvatarInterface:
- Отображение анимированного видео
- Элементы управления микрофоном
- Чат интерфейс с историей
- Индикаторы состояния (загрузка, ошибки)
- Поддержка эмодзи и эмоций
- Responsive дизайн с Tailwind CSS
```

### 3. Code Generation (Ctrl+K)

#### Автодополнение кода:
```
# Выделите функцию и нажмите Ctrl+K
"Добавь обработку ошибок GPU и логирование производительности"

# Для React компонентов:
"Добавь TypeScript типы и оптимизацию производительности с React.memo"

# Для Python функций:
"Добавь докстринги, type hints и валидацию входных данных"
```

### 4. Рефакторинг и оптимизация

#### Команды для оптимизации:
```
Ctrl+K -> "Оптимизируй этот код для работы с GPU RTX 3060 12GB"
Ctrl+K -> "Добавь кеширование результатов и управление памятью"
Ctrl+K -> "Рефактори код согласно SOLID принципам"
Ctrl+K -> "Добавь async/await для неблокирующих операций"
```

---

## 📝 Шаблоны промптов

### Для Python AI кода:
```
Создай Python класс для [ЗАДАЧА] с следующими требованиями:
- Оптимизация для RTX 3060 12GB VRAM
- Обработка ошибок и graceful degradation
- Логирование производительности
- Type hints для всех методов
- Docstrings с примерами использования
- Контекстные менеджеры для GPU ресурсов
```

### Для React компонентов:
```
Создай React компонент [НАЗВАНИЕ] с TypeScript:
- Функциональный компонент с hooks
- Оптимизация с React.memo, useCallback, useMemo
- Обработка ошибок с Error Boundary
- Responsive дизайн с Tailwind CSS
- Accessibility поддержка
- Состояния загрузки и ошибок
```

### Для API endpoints:
```
Создай FastAPI endpoint для [ФУНКЦИЯ]:
- Pydantic модели для валидации
- Async/await для неблокирующих операций
- Обработка файлов (аудио/видео)
- WebSocket поддержка для реального времени
- Логирование и мониторинг
- OpenAPI документация
```

---

## ⚙️ Настройка workspace

### 1. Создание multi-root workspace
```json
{
  "folders": [
    {
      "name": "Backend",
      "path": "./backend"
    },
    {
      "name": "Frontend",
      "path": "./frontend"
    },
    {
      "name": "AI Pipeline",
      "path": "./ai_pipeline"
    },
    {
      "name": "Scripts",
      "path": "./scripts"
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "./venv/bin/python"
  }
}
```

### 2. Создание задач (tasks.json)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && source ../venv/bin/activate && uvicorn app.main:app --reload",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Test GPU",
      "type": "shell",
      "command": "python scripts/test_gpu.py",
      "group": "test"
    },
    {
      "label": "Run Tests",
      "type": "shell",
      "command": "pytest backend/tests/",
      "group": "test"
    }
  ]
}
```

---

## 🔧 Полезные горячие клавиши

### Cursor специфичные:
- **Ctrl+L** - Открыть Cursor Chat
- **Ctrl+I** - Открыть Cursor Composer  
- **Ctrl+K** - Генерация кода
- **Ctrl+Shift+L** - Объяснить выделенный код
- **Ctrl+/** - Документировать код

### Общие:
- **Ctrl+Shift+P** - Command Palette
- **Ctrl+P** - Быстрый поиск файлов
- **Ctrl+Shift+F** - Поиск по проекту
- **Ctrl+`** - Открыть терминал
- **Ctrl+Shift+`** - Новый терминал

---

## 🎨 Настройка темы и интерфейса

### Рекомендуемые темы:
- **Dark+ (default dark)** - хорошо для AI/ML проектов
- **Monokai Pro** - отличная для Python
- **Material Theme** - современная для React

### Настройка шрифтов:
```json
{
  "editor.fontFamily": "'Fira Code', 'Consolas', 'Monaco', monospace",
  "editor.fontLigatures": true,
  "editor.fontSize": 14,
  "terminal.integrated.fontSize": 13
}
```

---

## 📊 Мониторинг и отладка

### Расширения для мониторинга:
- **Resource Monitor** - мониторинг системных ресурсов
- **GPU Usage** - мониторинг GPU (если доступно)
- **Python Profiler** - профилирование Python кода

### Настройка логирования:
```python
import logging
import sys

# Настройка логирования для AI операций
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_operations.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Специальные логгеры для разных компонентов
gpu_logger = logging.getLogger('gpu_operations')
ai_logger = logging.getLogger('ai_pipeline')
api_logger = logging.getLogger('api_calls')
```

---

## 🚀 Быстрый старт

### 1. Откройте проект в Cursor:
```bash
cd digital-avatar-system
cursor .
```

### 2. Настройте окружение:
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r backend/requirements.txt
```

### 3. Первые команды в Cursor Chat:
```
@codebase Проанализируй архитектуру проекта и подскажи с чего начать разработку

@codebase Создай базовую структуру FastAPI приложения согласно техническому заданию

@codebase Настрой интеграцию с первой AI моделью (Whisper для распознавания речи)
```

### 4. Проверка настроек:
- Откройте любой .py файл - должны работать автодополнение и подсказки
- Нажмите Ctrl+L и проверьте работу Cursor Chat
- Создайте простой Python файл и протестируйте Ctrl+K

---

## 🔍 Troubleshooting

### Проблема: Cursor не видит виртуальное окружение
**Решение:**
1. Ctrl+Shift+P → "Python: Select Interpreter"
2. Выберите `./venv/bin/python`

### Проблема: Медленная работа с большими файлами
**Решение:**
1. Проверьте .cursorignore - исключите большие файлы
2. Отключите индексацию ненужных папок в settings.json

### Проблема: AI не понимает контекст проекта
**Решение:**
1. Используйте `@codebase` в начале промптов
2. Создайте более подробные .cursorrules
3. Добавьте комментарии в ключевые файлы

---

**Cursor настроен и готов к работе! 🎉**

Теперь вы можете эффективно разрабатывать проект цифрового аватара с помощью AI-ассистента. 