#!/usr/bin/env python3
"""
Создание конфигурации для обучения YourTTS
"""

import os
from TTS.tts.configs.vits_config import VitsConfig

def create_yourtts_config():
    """Создаёт конфигурацию для обучения YourTTS"""
    
    # Создаём базовую конфигурацию VITS
    config = VitsConfig()
    
    # Настройки модели
    config.model = "vits"
    config.run_name = "voice_cloning_finetune"
    config.run_description = "Fine-tuning YourTTS на пользовательских данных"
    
    # Настройки датасета
    config.datasets = [
        {
            "name": "voice_cloning",
            "path": "training_data/wav",
            "meta_file_train": "training_data/metadata/train_metadata.csv",
            "meta_file_val": "training_data/metadata/val_metadata.csv",
            "language": "en"
        }
    ]
    
    # Настройки обучения
    config.training_params.batch_size = 8
    config.training_params.epochs = 1000
    config.training_params.learning_rate = 1e-4
    config.training_params.save_step = 1000
    config.training_params.eval_step = 500
    config.training_params.save_n_checkpoints = 5
    config.training_params.save_best_after = 10000
    config.training_params.target_loss = 0.5
    config.training_params.print_step = 25
    config.training_params.print_eval = True
    config.training_params.mixed_precision = True
    config.output_path = "tts_train_output"
    
    # Настройки для клонирования голоса
    config.use_speaker_encoder_as_loss = True
    config.speaker_encoder_model_path = None  # Будет загружена автоматически
    config.speaker_encoder_config_path = None
    
    # Настройки аудио
    config.audio.sample_rate = 22050
    config.audio.hop_length = 256
    config.audio.win_length = 1024
    config.audio.mel_fmin = 0
    config.audio.mel_fmax = 8000
    
    # Сохраняем конфигурацию
    config_path = "training_data/yourtts_config.json"
    config.save_json(config_path)
    
    print(f"✅ Конфигурация сохранена: {config_path}")
    return config_path

if __name__ == "__main__":
    create_yourtts_config() 