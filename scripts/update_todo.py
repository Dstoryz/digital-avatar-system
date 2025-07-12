#!/usr/bin/env python3
"""
Скрипт для автоматического обновления TODO-листа.

Использование:
    python scripts/update_todo.py --completed "Название выполненной задачи"
    python scripts/update_todo.py --add "Новая задача" --priority high
    python scripts/update_todo.py --stats
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

TODO_FILE = Path("TODO.md")
TEMPLATE_FILE = Path("TEMPLATES/todo_update_template.md")

def read_todo_file() -> str:
    """Чтение содержимого TODO.md."""
    if not TODO_FILE.exists():
        raise FileNotFoundError(f"Файл {TODO_FILE} не найден")
    
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def write_todo_file(content: str):
    """Запись содержимого в TODO.md."""
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

def find_todo_sections(content: str) -> Tuple[str, str, str]:
    """Поиск секций TODO файла."""
    # Разделяем на секции
    sections = content.split('## ')
    
    completed_section = ""
    in_progress_section = ""
    todo_section = ""
    
    for section in sections:
        if section.startswith('✅ Выполнено') or section.startswith('✅'):
            completed_section = section
        elif section.startswith('🔄 В работе') or section.startswith('🔄'):
            in_progress_section = section
        elif section.startswith('📋 Предстоит выполнить') or section.startswith('📋'):
            todo_section = section
    
    return completed_section, in_progress_section, todo_section

def mark_task_completed(content: str, task_name: str) -> str:
    """Отметить задачу как выполненную."""
    # Ищем задачу в секции "Предстоит выполнить"
    pattern = rf'(\s*)- \[ \] {re.escape(task_name)}'
    replacement = rf'\1- [x] {task_name} ({datetime.now().strftime("%Y-%m-%d")})'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        
        # Перемещаем задачу в секцию "Выполнено"
        # Находим секцию "Выполнено"
        completed_pattern = r'(## ✅ Выполнено.*?)(## 🔄 В работе)'
        match = re.search(completed_pattern, content, re.DOTALL)
        
        if match:
            completed_section = match.group(1)
            # Добавляем задачу в конец секции "Выполнено"
            new_completed_section = completed_section.rstrip() + f'\n- [x] {task_name} ({datetime.now().strftime("%Y-%m-%d")})\n\n'
            content = re.sub(completed_pattern, new_completed_section + r'\2', content, flags=re.DOTALL)
        
        print(f"✅ Задача '{task_name}' отмечена как выполненная")
    else:
        print(f"⚠️  Задача '{task_name}' не найдена в списке")
    
    return content

def add_new_task(content: str, task_name: str, priority: str = "medium", category: str = "Общее") -> str:
    """Добавить новую задачу."""
    priority_emoji = {
        "high": "🔥",
        "medium": "🔶", 
        "low": "🔵"
    }.get(priority, "🔶")
    
    new_task = f"- [ ] {priority_emoji} {task_name}"
    
    # Находим секцию "Предстоит выполнить"
    todo_pattern = r'(## 📋 Предстоит выполнить.*?)(## 🎯 Приоритеты)'
    match = re.search(todo_pattern, content, re.DOTALL)
    
    if match:
        todo_section = match.group(1)
        # Добавляем задачу в конец секции
        new_todo_section = todo_section.rstrip() + f'\n{new_task}\n\n'
        content = re.sub(todo_pattern, new_todo_section + r'\2', content, flags=re.DOTALL)
        
        print(f"➕ Добавлена новая задача: {priority_emoji} {task_name}")
    else:
        print("⚠️  Не удалось найти секцию 'Предстоит выполнить'")
    
    return content

def update_progress_stats(content: str) -> str:
    """Обновить статистику прогресса."""
    # Подсчитываем задачи
    completed_tasks = len(re.findall(r'- \[x\]', content))
    in_progress_tasks = len(re.findall(r'- \[ \].*🔄', content))
    todo_tasks = len(re.findall(r'- \[ \]', content)) - in_progress_tasks
    
    total_tasks = completed_tasks + in_progress_tasks + todo_tasks
    progress_percent = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    # Обновляем секцию прогресса
    progress_pattern = r'(## 📊 Прогресс\n\n- \*\*Выполнено\*\*: ).*?(\n- \*\*В работе\*\*: ).*?(\n- \*\*Предстоит\*\*: ).*?(\n- \*\*Общий прогресс\*\*: ).*?(\n\n---)'
    replacement = rf'\1{completed_tasks} задач ({round(completed_tasks/total_tasks*100, 1)}%)\2{in_progress_tasks} задач ({round(in_progress_tasks/total_tasks*100, 1)}%)\3{todo_tasks} задач ({round(todo_tasks/total_tasks*100, 1)}%)\4~{progress_percent}%\5'
    
    content = re.sub(progress_pattern, replacement, content)
    
    print(f"📊 Статистика обновлена: {completed_tasks}/{total_tasks} задач ({progress_percent}%)")
    return content

def update_last_modified(content: str, description: str, next_step: str = ""):
    """Обновить секцию 'Последнее обновление'."""
    last_modified_pattern = r'(---\n\n\*\*Последнее обновление\*\*: ).*?(\n\*\*Следующий этап\*\*: ).*?(\n)'
    
    if next_step:
        replacement = rf'\1{description}\2{next_step}\3'
    else:
        replacement = rf'\1{description}\2Продолжение разработки\3'
    
    content = re.sub(last_modified_pattern, replacement, content)
    return content

def show_stats(content: str):
    """Показать текущую статистику."""
    completed_tasks = len(re.findall(r'- \[x\]', content))
    in_progress_tasks = len(re.findall(r'- \[ \].*🔄', content))
    todo_tasks = len(re.findall(r'- \[ \]', content)) - in_progress_tasks
    
    total_tasks = completed_tasks + in_progress_tasks + todo_tasks
    progress_percent = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    print("📊 Текущая статистика проекта:")
    print(f"   ✅ Выполнено: {completed_tasks} задач")
    print(f"   🔄 В работе: {in_progress_tasks} задач")
    print(f"   📋 Предстоит: {todo_tasks} задач")
    print(f"   📈 Общий прогресс: {progress_percent}%")
    print(f"   📊 Всего задач: {total_tasks}")

def main():
    parser = argparse.ArgumentParser(description="Автоматическое обновление TODO-листа")
    parser.add_argument("--completed", help="Отметить задачу как выполненную")
    parser.add_argument("--add", help="Добавить новую задачу")
    parser.add_argument("--priority", choices=["high", "medium", "low"], default="medium", 
                       help="Приоритет новой задачи")
    parser.add_argument("--category", default="Общее", help="Категория новой задачи")
    parser.add_argument("--stats", action="store_true", help="Показать статистику")
    parser.add_argument("--description", help="Описание для 'Последнее обновление'")
    parser.add_argument("--next-step", help="Следующий этап")
    
    args = parser.parse_args()
    
    try:
        content = read_todo_file()
        
        if args.completed:
            content = mark_task_completed(content, args.completed)
        
        if args.add:
            content = add_new_task(content, args.add, args.priority, args.category)
        
        if args.completed or args.add:
            content = update_progress_stats(content)
            
            if args.description:
                content = update_last_modified(content, args.description, args.next_step)
            else:
                description = f"Обновлен TODO-лист"
                if args.completed:
                    description += f" - выполнена задача: {args.completed}"
                if args.add:
                    description += f" - добавлена задача: {args.add}"
                
                content = update_last_modified(content, description, args.next_step)
            
            write_todo_file(content)
            print("💾 TODO.md обновлен")
        
        if args.stats:
            show_stats(content)
        
        if not any([args.completed, args.add, args.stats]):
            parser.print_help()
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 