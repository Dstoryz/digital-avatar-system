#!/usr/bin/env python3
"""
Скрипт для детального анализа фотографий для цифрового аватара
Проверяет качество, освещение, фон и другие параметры
"""

import os
import sys
from PIL import Image, ImageStat
from typing import Dict, List, Tuple, Any
import json
from datetime import datetime

def analyze_brightness(image: Image.Image) -> float:
    """Анализ яркости изображения"""
    stat = ImageStat.Stat(image.convert('L'))
    return stat.mean[0]

def analyze_contrast(image: Image.Image) -> float:
    """Анализ контрастности изображения"""
    stat = ImageStat.Stat(image.convert('L'))
    return stat.stddev[0]

def analyze_color_distribution(image: Image.Image) -> Dict[str, float]:
    """Анализ распределения цветов"""
    # Конвертируем в RGB если нужно
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Получаем статистику по каналам
    stat = ImageStat.Stat(image)
    
    return {
        'red_mean': stat.mean[0],
        'green_mean': stat.mean[1], 
        'blue_mean': stat.mean[2],
        'red_std': stat.stddev[0],
        'green_std': stat.stddev[1],
        'blue_std': stat.stddev[2]
    }

def analyze_face_area_estimation(image: Image.Image) -> Dict[str, Any]:
    """Примерная оценка области лица (упрощенная)"""
    width, height = image.size
    
    # Предполагаем, что лицо находится в центральной части
    center_x, center_y = width // 2, height // 2
    face_size = min(width, height) // 3
    
    # Проверяем яркость в центральной области
    center_region = image.crop((
        center_x - face_size//2,
        center_y - face_size//2, 
        center_x + face_size//2,
        center_y + face_size//2
    ))
    
    center_brightness = analyze_brightness(center_region)
    overall_brightness = analyze_brightness(image)
    
    return {
        'center_brightness': center_brightness,
        'overall_brightness': overall_brightness,
        'brightness_ratio': center_brightness / overall_brightness if overall_brightness > 0 else 1,
        'face_area_estimated': face_size * face_size
    }

def get_image_format_info(image: Image.Image) -> Dict[str, Any]:
    """Получение информации о формате изображения"""
    return {
        'format': image.format,
        'mode': image.mode,
        'dpi': image.info.get('dpi', (None, None)),
        'exif': bool(image.getexif())
    }

def analyze_photo(filepath: str) -> Dict[str, Any]:
    """Полный анализ одной фотографии"""
    try:
        with Image.open(filepath) as image:
            width, height = image.size
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            
            # Базовые параметры
            aspect_ratio = width / height
            
            # Анализ качества
            brightness = analyze_brightness(image)
            contrast = analyze_contrast(image)
            colors = analyze_color_distribution(image)
            face_analysis = analyze_face_area_estimation(image)
            format_info = get_image_format_info(image)
            
            # Оценка качества
            quality_score = 0
            issues = []
            recommendations = []
            
            # Проверка разрешения
            if width >= 512 and height >= 512:
                quality_score += 2
            elif width >= 256 and height >= 256:
                quality_score += 1
                issues.append('Низкое разрешение')
                recommendations.append('Используйте фото с разрешением 512x512 или выше')
            else:
                issues.append('Очень низкое разрешение')
                recommendations.append('Фото слишком маленькое для качественного аватара')
            
            # Проверка размера файла
            if file_size >= 0.1:
                quality_score += 1
            else:
                issues.append('Маленький размер файла')
                recommendations.append('Возможно, фото слишком сжато')
            
            # Проверка соотношения сторон
            if 0.7 <= aspect_ratio <= 1.3:
                quality_score += 1
            else:
                issues.append('Необычное соотношение сторон')
                recommendations.append('Лучше использовать квадратные или близкие к квадрату фото')
            
            # Проверка яркости
            if 50 <= brightness <= 200:
                quality_score += 1
            elif brightness < 30:
                issues.append('Слишком темное фото')
                recommendations.append('Фото слишком темное, используйте лучше освещенные снимки')
            elif brightness > 220:
                issues.append('Слишком яркое фото')
                recommendations.append('Фото пересвечено, используйте фото с нормальным освещением')
            
            # Проверка контрастности
            if contrast >= 20:
                quality_score += 1
            else:
                issues.append('Низкая контрастность')
                recommendations.append('Фото слишком плоское, используйте фото с лучшим контрастом')
            
            # Проверка области лица
            if face_analysis['brightness_ratio'] >= 0.8:
                quality_score += 1
            else:
                issues.append('Проблемы с освещением лица')
                recommendations.append('Лицо может быть плохо освещено')
            
            return {
                'filename': os.path.basename(filepath),
                'filepath': filepath,
                'size': f'{width}x{height}',
                'file_size_mb': round(file_size, 2),
                'aspect_ratio': round(aspect_ratio, 2),
                'brightness': round(brightness, 1),
                'contrast': round(contrast, 1),
                'quality_score': quality_score,
                'max_score': 6,
                'issues': issues,
                'recommendations': recommendations,
                'face_analysis': face_analysis,
                'color_analysis': colors,
                'format_info': format_info,
                'status': '✅' if quality_score >= 4 else '⚠️' if quality_score >= 3 else '❌'
            }
            
    except Exception as e:
        return {
            'filename': os.path.basename(filepath),
            'filepath': filepath,
            'error': str(e),
            'status': '❌'
        }

def main():
    """Основная функция анализа"""
    photos_dir = 'test_data/photos'
    
    if not os.path.exists(photos_dir):
        print(f"❌ Папка {photos_dir} не найдена")
        return
    
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ФОТОГРАФИЙ ДЛЯ ЦИФРОВОГО АВАТАРА")
    print("=" * 60)
    
    # Получаем список файлов
    photo_files = []
    for filename in os.listdir(photos_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            photo_files.append(os.path.join(photos_dir, filename))
    
    if not photo_files:
        print("❌ Фотографии не найдены")
        return
    
    print(f"📸 Найдено фотографий: {len(photo_files)}")
    print()
    
    # Анализируем каждую фотографию
    results = []
    for filepath in photo_files:
        result = analyze_photo(filepath)
        results.append(result)
        
        # Выводим результат
        if 'error' in result:
            print(f"{result['status']} {result['filename']}: ОШИБКА - {result['error']}")
        else:
            print(f"{result['status']} {result['filename']}")
            print(f"   📏 Размер: {result['size']}")
            print(f"   📦 Вес: {result['file_size_mb']}MB")
            print(f"   📐 Соотношение: {result['aspect_ratio']}")
            print(f"   💡 Яркость: {result['brightness']}")
            print(f"   🎨 Контраст: {result['contrast']}")
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
        excellent = len([r for r in valid_results if r['quality_score'] >= 5])
        good = len([r for r in valid_results if r['quality_score'] >= 4])
        acceptable = len([r for r in valid_results if r['quality_score'] >= 3])
        poor = len([r for r in valid_results if r['quality_score'] < 3])
        
        print(f"   📸 Всего фото: {len(results)}")
        print(f"   ✅ Отличных (5-6 баллов): {excellent}")
        print(f"   🔶 Хороших (4 балла): {good}")
        print(f"   ⚠️  Приемлемых (3 балла): {acceptable}")
        print(f"   ❌ Плохих (<3 баллов): {poor}")
        print(f"   🎯 Средний балл: {avg_score:.1f}/6")
        
        # Рекомендации по улучшению
        print()
        print("💡 РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:")
        print("=" * 60)
        
        if poor > 0:
            print("❌ Некоторые фото требуют замены:")
            for r in valid_results:
                if r['quality_score'] < 3:
                    print(f"   - {r['filename']}: {', '.join(r['issues'])}")
        
        if avg_score < 4.5:
            print("🔶 Общие рекомендации:")
            print("   - Используйте фото с разрешением 512x512 или выше")
            print("   - Обеспечьте хорошее равномерное освещение")
            print("   - Избегайте резких теней на лице")
            print("   - Используйте нейтральный фон")
            print("   - Фото должны быть четкими и контрастными")
        
        if excellent >= len(valid_results) * 0.7:
            print("✅ Отличная подготовка! Фото готовы для создания аватара.")
        elif good >= len(valid_results) * 0.7:
            print("🔶 Хорошая подготовка. Можно начинать работу с аватаром.")
        else:
            print("⚠️  Требуется улучшение качества фото перед созданием аватара.")
    
    # Сохраняем результаты в JSON
    output_file = 'test_data/photo_analysis_results.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'total_photos': len(results),
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