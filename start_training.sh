#!/bin/bash

echo "🎤 Запуск обучения YourTTS на пользовательских данных"
echo "=================================================="

# Активируем окружение
source yourtts_env/bin/activate

# Проверяем наличие данных
if [ ! -d "training_data/wav" ]; then
    echo "❌ Папка training_data/wav не найдена!"
    exit 1
fi

if [ ! -f "training_data/metadata/train_metadata.csv" ]; then
    echo "❌ Файл train_metadata.csv не найден!"
    exit 1
fi

echo "✅ Данные найдены"
echo "🚀 Запуск обучения..."

# Запускаем обучение
python -m TTS.bin.train_tts \
    --config_path training_data/yourtts_config.json \
    --coqpit.datasets.0.path training_data/wav \
    --coqpit.datasets.0.meta_file_train training_data/metadata/train_metadata.csv \
    --coqpit.datasets.0.meta_file_val training_data/metadata/val_metadata.csv \
    --coqpit.training_params.batch_size 8 \
    --coqpit.training_params.epochs 1000 \
    --coqpit.training_params.learning_rate 1e-4 \
    --coqpit.training_params.save_step 1000 \
    --coqpit.training_params.eval_step 500 \
    --coqpit.training_params.print_step 25 \
    --coqpit.training_params.mixed_precision true \
    --coqpit.output_path tts_train_output

if [ $? -eq 0 ]; then
    echo "🎉 Обучение завершено успешно!"
    echo "📁 Результаты сохранены в: tts_train_output/"
    echo "🎤 Модель готова к использованию!"
else
    echo "❌ Обучение завершилось с ошибкой!"
    exit 1
fi 