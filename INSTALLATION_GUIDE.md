# РУКОВОДСТВО ПО УСТАНОВКЕ И НАСТРОЙКЕ

## Предварительные требования

### 1. Проверка системы
```bash
# Проверить версию CUDA
nvidia-smi

# Проверить версию Python
python3 --version

# Проверить доступность GPU
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
```

### 2. Установка необходимых пакетов
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3.10 python3.10-venv python3-pip -y

# Установка CUDA (если не установлен)
# Скачать с официального сайта NVIDIA
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

# Установка Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Установка Redis
sudo apt install redis-server -y

# Установка FFmpeg
sudo apt install ffmpeg -y
```

## Этап 1: Настройка окружения

### Создание проекта
```bash
# Создание структуры проекта
mkdir digital-avatar-system
cd digital-avatar-system

# Создание виртуального окружения Python
python3 -m venv venv
source venv/bin/activate

# Создание структуры папок
mkdir -p backend/app/api
mkdir -p backend/app/models
mkdir -p backend/app/services
mkdir -p backend/app/utils
mkdir -p backend/ai_pipeline/face_animation
mkdir -p backend/ai_pipeline/voice_cloning
mkdir -p backend/ai_pipeline/speech_recognition
mkdir -p backend/ai_pipeline/text_generation
mkdir -p frontend/src/components
mkdir -p frontend/src/hooks
mkdir -p frontend/src/services
mkdir -p frontend/src/utils
mkdir -p docker
mkdir -p scripts
mkdir -p data/images
mkdir -p data/audio
mkdir -p data/cache
```

### Установка Python зависимостей
```bash
# Создание requirements.txt
cat > backend/requirements.txt << 'EOF'
# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
websockets==12.0

# AI/ML
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
transformers==4.35.0
accelerate==0.24.1
diffusers==0.21.4
openai-whisper==20231117
TTS==0.20.6

# Computer Vision
opencv-python==4.8.1.78
Pillow==10.0.1
mediapipe==0.10.7
face-recognition==1.3.0

# Audio processing
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1

# Database and caching
redis==5.0.1
aioredis==2.0.1
sqlite3

# Utilities
numpy==1.24.3
scipy==1.11.4
requests==2.31.0
python-dotenv==1.0.0
aiofiles==23.2.1
python-socketio==5.10.0

# Development
pytest==7.4.3
black==23.10.1
flake8==6.1.0
EOF

# Установка зависимостей
pip install -r backend/requirements.txt
```

### Установка Node.js зависимостей
```bash
# Инициализация frontend
cd frontend
npm init -y

# Установка React и TypeScript
npm install react@18.2.0 react-dom@18.2.0 typescript@5.2.2
npm install @types/react@18.2.37 @types/react-dom@18.2.15
npm install -D @vitejs/plugin-react@4.1.1 vite@4.5.0

# Установка дополнительных пакетов
npm install socket.io-client@4.7.2
npm install tailwindcss@3.3.5 autoprefixer@10.4.16 postcss@8.4.31
npm install framer-motion@10.16.4
npm install @heroicons/react@2.0.18
npm install react-router-dom@6.18.0
npm install axios@1.6.0

# Настройка Tailwind CSS
npx tailwindcss init -p
```

## Этап 2: Установка AI моделей

### Установка Ollama
```bash
# Установка Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Скачивание Llama 3.2 8B
ollama pull llama3.2:8b
```

### Установка SadTalker
```bash
cd backend/ai_pipeline/face_animation

# Клонирование репозитория SadTalker
git clone https://github.com/OpenTalker/SadTalker.git
cd SadTalker

# Установка зависимостей
pip install -r requirements.txt

# Скачивание предобученных моделей
mkdir checkpoints
cd checkpoints

# Скачивание модели SadTalker
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors
```

### Установка Real-ESRGAN
```bash
cd backend/ai_pipeline/

# Клонирование Real-ESRGAN
git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN

# Установка
pip install basicsr
pip install facexlib
pip install gfpgan
pip install -r requirements.txt
python setup.py develop

# Скачивание предобученных моделей
mkdir models
cd models
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
```

## Этап 3: Настройка конфигурации

### Создание файла окружения
```bash
# Создание .env файла
cat > backend/.env << 'EOF'
# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Database
DATABASE_URL=sqlite:///./data/database.db

# Redis
REDIS_URL=redis://localhost:6379

# AI Models
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Paths
DATA_DIR=./data
CACHE_DIR=./data/cache
MODELS_DIR=./ai_pipeline

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:8b

# Performance
MAX_WORKERS=4
BATCH_SIZE=1
GPU_MEMORY_FRACTION=0.8
EOF
```

### Создание конфигурационного файла
```bash
cat > backend/config.py << 'EOF'
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./data/database.db"
    redis_url: str = "redis://localhost:6379"
    
    # AI Models
    cuda_visible_devices: str = "0"
    pytorch_cuda_alloc_conf: str = "max_split_size_mb:512"
    
    # Paths
    data_dir: str = "./data"
    cache_dir: str = "./data/cache"
    models_dir: str = "./ai_pipeline"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:8b"
    
    # Performance
    max_workers: int = 4
    batch_size: int = 1
    gpu_memory_fraction: float = 0.8
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF
```

## Этап 4: Тестирование установки

### Тест GPU
```bash
# Создание скрипта тестирования GPU
cat > scripts/test_gpu.py << 'EOF'
import torch
import psutil
import GPUtil

print("=== Системная информация ===")
print(f"CPU: {psutil.cpu_count()} ядер")
print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")

print("\n=== CUDA информация ===")
print(f"CUDA доступен: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA версия: {torch.version.cuda}")
    print(f"Количество GPU: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        gpu = torch.cuda.get_device_properties(i)
        print(f"GPU {i}: {gpu.name}")
        print(f"  Память: {gpu.total_memory / (1024**3):.1f} GB")
        print(f"  Compute capability: {gpu.major}.{gpu.minor}")

print("\n=== Тест производительности ===")
if torch.cuda.is_available():
    device = torch.device('cuda')
    # Простой тест матричного умножения
    size = 1000
    a = torch.randn(size, size, device=device)
    b = torch.randn(size, size, device=device)
    
    import time
    start = time.time()
    c = torch.matmul(a, b)
    torch.cuda.synchronize()
    end = time.time()
    
    print(f"Матричное умножение {size}x{size}: {end-start:.4f} секунд")
    print(f"Используемая память GPU: {torch.cuda.memory_allocated()/1024**3:.2f} GB")
EOF

# Запуск теста
python scripts/test_gpu.py
```

### Тест моделей
```bash
# Создание скрипта тестирования моделей
cat > scripts/test_models.py << 'EOF'
import torch
import whisper
import requests
import time

print("=== Тестирование моделей ===")

# Тест Whisper
print("\n1. Тестирование Whisper...")
try:
    model = whisper.load_model("base")
    print("✓ Whisper модель загружена успешно")
    
    # Тест на простом файле
    # result = model.transcribe("test_audio.wav")
    # print(f"Результат: {result['text']}")
except Exception as e:
    print(f"✗ Ошибка Whisper: {e}")

# Тест Ollama
print("\n2. Тестирование Ollama...")
try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:8b",
            "prompt": "Привет! Как дела?",
            "stream": False
        }
    )
    if response.status_code == 200:
        print("✓ Ollama работает корректно")
        result = response.json()
        print(f"Ответ: {result.get('response', 'Нет ответа')}")
    else:
        print(f"✗ Ollama недоступен: {response.status_code}")
except Exception as e:
    print(f"✗ Ошибка Ollama: {e}")

# Тест PyTorch
print("\n3. Тестирование PyTorch...")
try:
    if torch.cuda.is_available():
        device = torch.device('cuda')
        x = torch.randn(100, 100, device=device)
        y = torch.randn(100, 100, device=device)
        z = torch.matmul(x, y)
        print("✓ PyTorch с CUDA работает корректно")
    else:
        print("✗ CUDA недоступен для PyTorch")
except Exception as e:
    print(f"✗ Ошибка PyTorch: {e}")

print("\n=== Тестирование завершено ===")
EOF

# Запуск теста моделей
python scripts/test_models.py
```

## Этап 5: Запуск системы

### Запуск Redis
```bash
# Запуск Redis сервера
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Проверка статуса
redis-cli ping
```

### Запуск Ollama
```bash
# Запуск Ollama в фоновом режиме
ollama serve &

# Проверка работы
curl http://localhost:11434/api/version
```

### Запуск backend
```bash
cd backend
source ../venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Запуск frontend
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Проблемы с CUDA
```bash
# Проверка драйверов
nvidia-smi

# Переустановка CUDA
sudo apt-get --purge remove "*cublas*" "*cufft*" "*curand*" "*cusolver*" "*cusparse*" "*npp*" "*nvjpeg*" "cuda*" "nsight*"
sudo apt-get autoremove
# Повторная установка по инструкции выше
```

### Проблемы с памятью GPU
```bash
# Очистка кеша GPU
python -c "import torch; torch.cuda.empty_cache()"

# Мониторинг использования GPU
watch -n 1 nvidia-smi
```

### Проблемы с моделями
```bash
# Очистка кеша моделей
rm -rf ~/.cache/huggingface/
rm -rf ~/.cache/torch/

# Повторная загрузка моделей
python -c "import whisper; whisper.load_model('base')"
```

Система готова к разработке! Следуйте техническому заданию для дальнейших этапов. 