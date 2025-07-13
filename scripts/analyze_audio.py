#!/usr/bin/env python3
"""
Скрипт для детального анализа аудиофайлов для цифрового аватара
Проверяет качество, длительность, частоту дискретизации и другие параметры
"""

import os
import sys
import json
from typing import Dict, List, Any
from datetime import datetime
import subprocess
import re

def get_audio_info(filepath: str) -> Dict[str, Any]:
    """Получение информации об аудиофайле с помощью ffprobe"""
    try:
        # Используем ffprobe для получения информации об аудио
        cmd = [
            'ffprobe', 
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            filepath
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Извлекаем информацию
        format_info = data.get('format', {})
        audio_stream = None
        
        # Ищем аудио поток
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        if not audio_stream:
            raise Exception("Аудио поток не найден")
        
        # Получаем основные параметры
        duration = float(format_info.get('duration', 0))
        file_size = float(format_info.get('size', 0)) / (1024 * 1024)  # MB
        bit_rate = int(format_info.get('bit_rate', 0)) / 1000 if format_info.get('bit_rate') else 0  # kbps
        
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 1))
        codec = audio_stream.get('codec_name', 'unknown')
        
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'duration_seconds': duration,
            'duration_formatted': format_duration(duration),
            'file_size_mb': round(file_size, 2),
            'bit_rate_kbps': round(bit_rate, 1),
            'sample_rate_hz': sample_rate,
            'channels': channels,
            'codec': codec,
            'format': format_info.get('format_name', 'unknown')
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'error': f"Ошибка ffprobe: {e.stderr}"
        }
    except Exception as e:
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'error': str(e)
        }

def format_duration(seconds: float) -> str:
    """Форматирование длительности в читаемый вид"""
    if seconds < 60:
        return f"{seconds:.1f}с"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}м {secs:.1f}с"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}ч {minutes}м {secs:.1f}с"

def analyze_audio_quality(audio_info: Dict[str, Any]) -> Dict[str, Any]:
    """Анализ качества аудиофайла"""
    if 'error' in audio_info:
        return {
            'quality_score': 0,
            'max_score': 6,
            'issues': ['Ошибка чтения файла'],
            'recommendations': ['Проверьте целостность файла'],
            'status': '❌'
        }
    
    quality_score = 0
    issues = []
    recommendations = []
    
    # Проверка длительности
    duration = audio_info['duration_seconds']
    if duration >= 30:  # 30 секунд или больше
        quality_score += 2
    elif duration >= 10:  # 10-30 секунд
        quality_score += 1
        issues.append('Короткая длительность')
        recommendations.append('Рекомендуется запись длительностью 30+ секунд')
    else:
        issues.append('Очень короткая запись')
        recommendations.append('Запись слишком короткая для обучения')
    
    # Проверка частоты дискретизации
    sample_rate = audio_info['sample_rate_hz']
    if sample_rate >= 44100:
        quality_score += 2
    elif sample_rate >= 22050:
        quality_score += 1
        issues.append('Низкая частота дискретизации')
        recommendations.append('Рекомендуется 44.1kHz или выше')
    else:
        issues.append('Очень низкая частота дискретизации')
        recommendations.append('Качество звука может быть недостаточным')
    
    # Проверка битрейта
    bit_rate = audio_info['bit_rate_kbps']
    if bit_rate >= 128:
        quality_score += 1
    elif bit_rate >= 64:
        quality_score += 0.5
        issues.append('Низкий битрейт')
        recommendations.append('Рекомендуется битрейт 128kbps или выше')
    else:
        issues.append('Очень низкий битрейт')
        recommendations.append('Качество сжатия может быть недостаточным')
    
    # Проверка количества каналов
    channels = audio_info['channels']
    if channels == 1:
        quality_score += 1
        # Моно - хорошо для TTS
    elif channels == 2:
        quality_score += 0.5
        issues.append('Стерео запись')
        recommendations.append('Моно запись предпочтительнее для TTS')
    else:
        issues.append('Многоканальная запись')
        recommendations.append('Используйте моно или стерео запись')
    
    # Определяем статус
    if quality_score >= 4:
        status = '✅'
    elif quality_score >= 2:
        status = '⚠️'
    else:
        status = '❌'
    
    return {
        'quality_score': quality_score,
        'max_score': 6,
        'issues': issues,
        'recommendations': recommendations,
        'status': status
    }

def main():
    """Основная функция анализа"""
    audio_dir = 'test_data/audio'
    
    if not os.path.exists(audio_dir):
        print(f"❌ Папка {audio_dir} не найдена")
        return
    
    print("🎤 ДЕТАЛЬНЫЙ АНАЛИЗ АУДИОФАЙЛОВ ДЛЯ ЦИФРОВОГО АВАТАРА")
    print("=" * 60)
    
    # Получаем список файлов
    audio_files = []
    for filename in os.listdir(audio_dir):
        if filename.lower().endswith(('.ogg', '.wav', '.mp3', '.m4a', '.flac')):
            audio_files.append(os.path.join(audio_dir, filename))
    
    if not audio_files:
        print("❌ Аудиофайлы не найдены")
        return
    
    print(f"🎵 Найдено аудиофайлов: {len(audio_files)}")
    print()
    
    # Анализируем каждый файл
    results = []
    total_duration = 0
    
    for filepath in audio_files:
        audio_info = get_audio_info(filepath)
        quality_analysis = analyze_audio_quality(audio_info)
        
        result = {**audio_info, **quality_analysis}
        results.append(result)
        
        if 'error' not in audio_info:
            total_duration += audio_info['duration_seconds']
        
        # Выводим результат
        if 'error' in audio_info:
            print(f"{result['status']} {result['filename']}: ОШИБКА - {result['error']}")
        else:
            print(f"{result['status']} {result['filename']}")
            print(f"   ⏱️  Длительность: {result['duration_formatted']}")
            print(f"   📦 Размер: {result['file_size_mb']}MB")
            print(f"   🎵 Частота: {result['sample_rate_hz']}Hz")
            print(f"   🔊 Каналы: {result['channels']}")
            print(f"   📊 Битрейт: {result['bit_rate_kbps']}kbps")
            print(f"   🎯 Качество: {result['quality_score']}/{result['max_score']}")
            
            if result['issues']:
                print(f"   ⚠️  Проблемы: {', '.join(result['issues'])}")
            if result['recommendations']:
                print(f"   💡 Рекомендации: {', '.join(result['recommendations'])}")
        print()
    
    # Общая статистика
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        print("📊 ОБЩАЯ СТАТИСТИКА")
        print("=" * 60)
        
        avg_score = sum(r['quality_score'] for r in valid_results) / len(valid_results)
        excellent = len([r for r in valid_results if r['quality_score'] >= 4])
        good = len([r for r in valid_results if r['quality_score'] >= 3])
        acceptable = len([r for r in valid_results if r['quality_score'] >= 2])
        poor = len([r for r in valid_results if r['quality_score'] < 2])
        
        total_duration_minutes = total_duration / 60
        
        print(f"   🎵 Всего файлов: {len(results)}")
        print(f"   ✅ Отличных (4-6 баллов): {excellent}")
        print(f"   🔶 Хороших (3 балла): {good}")
        print(f"   ⚠️  Приемлемых (2 балла): {acceptable}")
        print(f"   ❌ Плохих (<2 баллов): {poor}")
        print(f"   🎯 Средний балл: {avg_score:.1f}/6")
        print(f"   ⏱️  Общая длительность: {total_duration_minutes:.1f} минут")
        
        # Рекомендации по улучшению
        print()
        print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        print("=" * 60)
        
        if poor > 0:
            print("❌ Некоторые файлы требуют замены:")
            for r in valid_results:
                if r['quality_score'] < 2:
                    print(f"   - {r['filename']}: {', '.join(r['issues'])}")
        
        if total_duration_minutes < 5:
            print("⚠️  Недостаточно аудиоматериала:")
            print(f"   - Текущая длительность: {total_duration_minutes:.1f} минут")
            print("   - Рекомендуется: 5-10 минут")
            print("   - Добавьте больше аудиозаписей")
        
        if avg_score < 4:
            print("🔶 Общие рекомендации:")
            print("   - Используйте частоту дискретизации 44.1kHz или выше")
            print("   - Записывайте в моно формате")
            print("   - Используйте битрейт 128kbps или выше")
            print("   - Записывайте фразы длительностью 30+ секунд")
            print("   - Избегайте фонового шума")
        
        if excellent >= len(valid_results) * 0.7 and total_duration_minutes >= 5:
            print("✅ Отличная подготовка! Аудио готово для клонирования голоса.")
        elif good >= len(valid_results) * 0.7 and total_duration_minutes >= 3:
            print("🔶 Хорошая подготовка. Можно начинать обучение TTS.")
        else:
            print("⚠️  Требуется улучшение качества аудио перед обучением TTS.")
    
    # Сохраняем результаты в JSON
    output_file = 'test_data/audio_analysis_results.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_files': len(results),
            'total_duration_minutes': total_duration / 60 if valid_results else 0,
            'results': results,
            'summary': {
                'avg_score': avg_score if valid_results else 0,
                'excellent_count': excellent if valid_results else 0,
                'good_count': good if valid_results else 0,
                'acceptable_count': acceptable if valid_results else 0,
                'poor_count': poor if valid_results else 0
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в {output_file}")

if __name__ == "__main__":
    main() 