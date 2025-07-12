"""
Конфигурация приложения для системы цифрового аватара.

Содержит настройки окружения, базы данных, Redis, AI моделей и безопасности.

Автор: Авабот
Версия: 1.0.0
"""

import os
from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Сервер
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # База данных
    DATABASE_URL: str = "sqlite:///./data/avatar.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI модели
    MODELS_PATH: str = "./data/models"
    CACHE_PATH: str = "./data/cache"
    
    # GPU
    USE_GPU: bool = True
    CUDA_VISIBLE_DEVICES: str = "0"
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Ограничения
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_AUDIO_DURATION: int = 300  # 5 минут
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Парсинг CORS origins из строки."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Парсинг allowed hosts из строки."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Создание экземпляра настроек
settings = Settings() 