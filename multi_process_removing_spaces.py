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
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
            return filepath, True, "изменен"
        else:
            return filepath, True, "без изменений"
            
    except Exception as e:
        return filepath, False, str(e)

def process_single_file_wrapper(filepath):
    """
    Обертка для обработки одного файла
    """
    return process_file_inplace(filepath)

def main():
    base_dir = "ecodpo.ru"
    
    print("=" * 60)
    print("Обработка HTML файлов на месте")
    print(f"Директория: {base_dir}")
    print("Используем 30 потоков для обработки")
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
    
    # Статистика
    stats = {
        'total': len(html_files),
        'modified': 0,
        'unchanged': 0,
        'errors': 0,
        'processed': 0
    }
    
    start_time = time.time()
    
    # Создаем пул из 30 потоков
    max_workers = 30
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Создаем задачи для каждого файла
        future_to_file = {executor.submit(process_single_file_wrapper, filepath): filepath 
                         for filepath in html_files}
        
        # Обрабатываем результаты по мере готовности
        for i, future in enumerate(as_completed(future_to_file), 1):
            try:
                filepath, success, message = future.result()
                rel_path = os.path.relpath(filepath, base_dir)
                stats['processed'] += 1
                
                if success:
                    if "изменен" in message:
                        stats['modified'] += 1
                        print(f"[{i}/{len(html_files)}] ✓ {rel_path}")
                    else:
                        stats['unchanged'] += 1
                        # Выводим только каждый 50-й неизмененный файл для уменьшения шума
                        if i % 50 == 0:
                            print(f"[{i}/{len(html_files)}] ○ {rel_path}")
                else:
                    stats['errors'] += 1
                    print(f"[{i}/{len(html_files)}] ✗ {rel_path}: {message}")
                
                # Выводим прогресс каждые 100 файлов
                if i % 100 == 0:
                    elapsed_time = time.time() - start_time
                    files_per_second = i / elapsed_time
                    estimated_total = elapsed_time * len(html_files) / i if i > 0 else 0
                    remaining = estimated_total - elapsed_time
                    
                    print(f"Прогресс: {i}/{len(html_files)} ({i/len(html_files)*100:.1f}%) | "
                          f"Скорость: {files_per_second:.1f} файл/сек | "
                          f"Осталось: {remaining:.0f} сек")
                    
            except Exception as e:
                stats['errors'] += 1
                print(f"[{i}/{len(html_files)}] ✗ Ошибка при обработке: {e}")
    
    elapsed_time = time.time() - start_time
    
    # Вывод статистики
    print("\n" + "=" * 60)
    print("СТАТИСТИКА:")
    print(f"  Всего файлов: {stats['total']}")
    print(f"  Обработано: {stats['processed']}")
    print(f"  Изменено: {stats['modified']}")
    print(f"  Без изменений: {stats['unchanged']}")
    print(f"  Ошибок: {stats['errors']}")
    print(f"  Время выполнения: {elapsed_time:.2f} секунд")
    if elapsed_time > 0:
        print(f"  Скорость обработки: {stats['total']/elapsed_time:.1f} файлов/сек")
    print("=" * 60)

if __name__ == "__main__":
    main()
