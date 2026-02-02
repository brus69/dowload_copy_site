#!/usr/bin/env python3
"""
Скрипт для рекурсивной обработки HTML файлов на месте
Модифицирует файлы прямо в директории /ecodpo
"""

import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import tempfile

def add_spaces_to_body(html_content):
    """
    Добавляет пробелы между тегами внутри body
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        if not soup.body:
            return html_content
        
        # Получаем содержимое body
        body_str = str(soup.body)
        
        # Паттерн: >< где следующий тег не закрывающий
        pattern = r'(>)(\s*)(<)(?!/)'
        
        # Заменяем >< на > <
        modified_body = re.sub(pattern, r'> \2', body_str)
        
        # Обновляем только body
        body_soup = BeautifulSoup(modified_body, 'html.parser')
        soup.body.clear()
        
        # Переносим все дочерние элементы в исходный body
        for child in body_soup.body.children:
            soup.body.append(child)
        
        return str(soup)
    
    except Exception as e:
        print(f"  Ошибка обработки: {e}")
        return html_content

def process_file_inplace(filepath):
    """
    Обрабатывает один файл на месте с созданием временной копии
    """
    try:
        # Читаем оригинальный файл
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
        
        # Получаем хеш оригинального содержимого (для сравнения)
        original_hash = hashlib.md5(original_content.encode('utf-8')).hexdigest()
        
        # Обрабатываем
        modified_content = add_spaces_to_body(original_content)
        modified_hash = hashlib.md5(modified_content.encode('utf-8')).hexdigest()
        
        # Если содержимое изменилось - сохраняем
        if original_hash != modified_hash:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(
                mode='w', 
                encoding='utf-8',
                dir=os.path.dirname(filepath),
                delete=False,
                suffix='.tmp'
            ) as tmp:
                tmp.write(modified_content)
                temp_name = tmp.name
            
            # Заменяем оригинальный файл
            os.replace(temp_name, filepath)
            return True, "изменен"
        else:
            return True, "без изменений"
            
    except Exception as e:
        return False, str(e)

def main():
    base_dir = "ecodpo.ru"
    
    print("=" * 60)
    print("Обработка HTML файлов на месте")
    print(f"Директория: {base_dir}")
    print("=" * 60)
    
    # Проверяем существование директории
    if not os.path.exists(base_dir):
        print(f"Ошибка: Директория {base_dir} не существует!")
        sys.exit(1)
    
    # Находим все HTML файлы
    html_extensions = {'.html', '.htm', '.xhtml', '.HTML', '.HTM', '.XHTML'}
    html_files = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if any(file.endswith(ext) for ext in html_extensions):
                full_path = os.path.join(root, file)
                html_files.append(full_path)
    
    if not html_files:
        print("HTML файлы не найдены!")
        return
    
    print(f"Найдено {len(html_files)} HTML файлов\n")
    
    # Обрабатываем файлы
    stats = {
        'total': len(html_files),
        'modified': 0,
        'unchanged': 0,
        'errors': 0
    }
    
    for i, filepath in enumerate(html_files, 1):
        # Выводим относительный путь для читаемости
        rel_path = os.path.relpath(filepath, base_dir)
        print(f"[{i}/{len(html_files)}] {rel_path}...", end=" ", flush=True)
        
        success, message = process_file_inplace(filepath)
        
        if success:
            if "изменен" in message:
                print("✓ изменен")
                stats['modified'] += 1
            else:
                print("○ без изменений")
                stats['unchanged'] += 1
        else:
            print(f"✗ ошибка: {message}")
            stats['errors'] += 1
    
    # Вывод статистики
    print("\n" + "=" * 60)
    print("СТАТИСТИКА:")
    print(f"  Всего файлов: {stats['total']}")
    print(f"  Изменено: {stats['modified']}")
    print(f"  Без изменений: {stats['unchanged']}")
    print(f"  Ошибок: {stats['errors']}")
    print("=" * 60)

if __name__ == "__main__":
    main()
