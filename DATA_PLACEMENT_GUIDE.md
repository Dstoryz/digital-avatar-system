# 📁 Руководство по размещению фото и аудио файлов

## 🗂️ Структура папок

```
test_data/
├── photos/              # Исходные фотографии
│   ├── avatar_front.jpg
│   ├── avatar_side.jpg
│   └── avatar_profile.jpg
├── audio/               # Исходные аудиосэмплы
│   ├── happy_speech.wav
│   ├── calm_speech.wav
│   └── surprised_speech.wav
└── processed/           # Обработанные файлы
    ├── avatars/         # Оптимизированные фото для AI
    ├── voice_clips/     # Обработанные аудиофайлы
    └── animations/      # Готовые анимации
```

## 📸 Размещение фотографий

### Папка: `test_data/photos/`

**Что размещать:**
- Исходные фотографии девочки
- 3-5 качественных фото
- Разрешение: 512x512 или выше

**Требования к файлам:**
- **Форматы**: JPG, PNG, WEBP
- **Размер**: максимум 10MB каждое
- **Качество**: высокое, без сжатия

**Рекомендуемые имена файлов:**
```
avatar_front.jpg      # Фото анфас
avatar_side.jpg       # Фото в профиль
avatar_profile.jpg    # Фото для профиля
avatar_closeup.jpg    # Крупный план лица
avatar_full.jpg       # Полное фото
```

**Пример размещения:**
```bash
# Скопировать фото в папку
cp /path/to/your/photo.jpg test_data/photos/avatar_front.jpg
cp /path/to/your/photo2.jpg test_data/photos/avatar_side.jpg
cp /path/to/your/photo3.jpg test_data/photos/avatar_profile.jpg
```

## 🎤 Размещение аудиосэмплов

### Папка: `test_data/audio/`

**Что размещать:**
- Исходные аудиозаписи девочки
- 5-10 минут общей речи
- Разные эмоции и интонации

**Требования к файлам:**
- **Форматы**: WAV, MP3, M4A
- **Частота**: 16kHz или выше
- **Качество**: 16-bit или выше
- **Длительность**: 2-5 минут каждый файл

**Рекомендуемые имена файлов:**
```
happy_speech.wav       # Радостная речь
calm_speech.wav        # Спокойная речь
surprised_speech.wav   # Удивленная речь
normal_speech.wav      # Обычная речь
questions_speech.wav   # Вопросы
```

**Пример размещения:**
```bash
# Скопировать аудио в папку
cp /path/to/your/happy.wav test_data/audio/happy_speech.wav
cp /path/to/your/calm.wav test_data/audio/calm_speech.wav
cp /path/to/your/surprised.wav test_data/audio/surprised_speech.wav
```

## 🔄 Обработанные файлы

### Папка: `test_data/processed/avatars/`
- Оптимизированные фото для SadTalker
- Размер: 512x512
- Формат: JPG
- Автоматически создаются системой

### Папка: `test_data/processed/voice_clips/`
- Обработанные аудиофайлы
- Нормализованные по громкости
- Подготовленные для Coqui TTS
- Автоматически создаются системой

### Папка: `test_data/processed/animations/`
- Готовые анимации лица
- Видеофайлы с анимированным аватаром
- Автоматически создаются системой

## 🚀 Практические шаги

### Шаг 1: Создать папки (уже сделано)
```bash
mkdir -p test_data/{photos,audio,processed/{avatars,voice_clips,animations}}
```

### Шаг 2: Подготовить фото
1. Сделать 3-5 качественных фото девочки
2. Проверить требования (разрешение, качество, освещение)
3. Скопировать в `test_data/photos/`
4. Переименовать по шаблону

### Шаг 3: Подготовить аудио
1. Записать 5-10 минут речи
2. Разделить на файлы по эмоциям
3. Проверить качество (частота, отсутствие шума)
4. Скопировать в `test_data/audio/`
5. Переименовать по шаблону

### Шаг 4: Проверить размещение
```bash
# Проверить структуру
tree test_data/

# Проверить фото
ls -la test_data/photos/
# Должно быть 3-5 файлов

# Проверить аудио
ls -la test_data/audio/
# Должно быть 3-5 файлов, общая длительность 5-10 минут
```

## 📋 Чек-лист размещения

### Фото файлы:
- [ ] 3-5 файлов в `test_data/photos/`
- [ ] Разрешение минимум 512x512
- [ ] Формат JPG, PNG или WEBP
- [ ] Понятные имена файлов
- [ ] Качество соответствует требованиям

### Аудио файлы:
- [ ] 3-5 файлов в `test_data/audio/`
- [ ] Общая длительность 5-10 минут
- [ ] Частота 16kHz или выше
- [ ] Разные эмоции включены
- [ ] Понятные имена файлов

### Структура папок:
- [ ] Создана папка `test_data/`
- [ ] Создана папка `test_data/photos/`
- [ ] Создана папка `test_data/audio/`
- [ ] Создана папка `test_data/processed/`
- [ ] Созданы подпапки в `processed/`

## 🔧 Полезные команды

### Проверка файлов
```bash
# Проверить размер и разрешение фото
file test_data/photos/*.jpg

# Проверить длительность аудио
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 test_data/audio/*.wav

# Проверить частоту аудио
ffprobe -v quiet -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 test_data/audio/*.wav
```

### Копирование файлов
```bash
# Копировать фото
cp /path/to/photo.jpg test_data/photos/avatar_front.jpg

# Копировать аудио
cp /path/to/audio.wav test_data/audio/happy_speech.wav

# Копировать все файлы определенного типа
cp /path/to/photos/*.jpg test_data/photos/
cp /path/to/audio/*.wav test_data/audio/
```

## ⚠️ Важные замечания

1. **Не изменяйте** файлы в папке `processed/` - они создаются автоматически
2. **Сохраняйте оригиналы** в папках `photos/` и `audio/`
3. **Проверяйте качество** перед размещением
4. **Используйте понятные имена** файлов
5. **Следуйте требованиям** по форматам и размерам

## 🎯 Результат

После правильного размещения у вас будет:
- ✅ Структурированные данные для AI моделей
- ✅ Готовность к загрузке в систему
- ✅ Возможность автоматической обработки
- ✅ Основа для создания цифрового аватара

---

**💡 Совет**: Храните резервные копии оригинальных файлов в отдельной папке! 