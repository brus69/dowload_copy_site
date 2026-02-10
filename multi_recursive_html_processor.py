#!/usr/bin/env python3
"""
Скрипт для рекурсивной обработки HTML файлов на месте
Модифицирует файлы прямо в директории
"""

import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import tempfile
import logging
from tqdm import tqdm  # Для отображения прогресс-бара

# Настройка логгера
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # Создаем директорию logs, если её нет
LOG_FILE = LOG_DIR / "recursive_html_processor.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)

logger = logging.getLogger("html_processor")

# Компиляция регулярного выражения заранее
SPACE_PATTERN = re.compile(r'(\s*)(>)(\s*)')

def add_spaces_to_body(html_content):
    """Прямая обработка всего документа"""
    try:
        return SPACE_PATTERN.sub(r'\1\2 \3', html_content)
    except Exception as e:
        logger.error(f"Ошибка обработки: {e}")
        return html_content


def process_file_inplace(filepath):
    """
    Обрабатывает один файл на месте с созданием временной копии
    """
    try:
        # Читаем оригинальный файл
        original_content = filepath.read_text(encoding='utf-8', errors='ignore')
        
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
                dir=filepath.parent,
                delete=False,
                suffix='.tmp'
            ) as tmp:
                tmp.write(modified_content)
                temp_name = tmp.name
            
            # Заменяем оригинальный файл
            Path(temp_name).replace(filepath)
            return True, "изменен"
        else:
            return True, "без изменений"
            
    except Exception as e:
        return False, str(e)


def main():
    base_dir = input("Введите название каталога: ").strip()
    base_path = Path(base_dir)
    
    print("=" * 60)
    print("Обработка HTML файлов на месте")
    print(f"Директория: {base_dir}")
    print("=" * 60)
    
    # Проверяем существование директории
    if not base_path.exists():
        logger.error(f"Ошибка: Директория {base_dir} не существует!")
        sys.exit(1)
    
    # Находим все HTML файлы
    html_extensions = {'.html', '.htm', '.xhtml', '.HTML', '.HTM', '.XHTML'}
    html_files = list(base_path.rglob('*.*'))  # Рекурсивный поиск
    html_files = [f for f in html_files if f.suffix in html_extensions]
    
    if not html_files:
        logger.info("HTML файлы не найдены!")
        return
    
    print(f"Найдено {len(html_files)} HTML файлов\n")
    
    # Статистика
    stats = {
        'total': len(html_files),
        'modified': 0,
        'unchanged': 0,
        'errors': 0
    }
    
    # Многопоточная обработка
    with ThreadPoolExecutor(max_workers=18) as executor:
        futures = {
            executor.submit(process_file_inplace, file): file
            for file in html_files
        }
        
        # Отображаем прогресс
        for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка файлов"):
            filepath = futures[future]
            rel_path = filepath.relative_to(base_path)
            
            try:
                success, message = future.result()
                if success:
                    if "изменен" in message:
                        stats['modified'] += 1
                    else:
                        stats['unchanged'] += 1
                else:
                    stats['errors'] += 1
                    logger.error(f"Ошибка при обработке файла {rel_path}: {message}")
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Неожиданная ошибка при обработке файла {rel_path}: {e}")
    
    # Вывод статистики
    print("\n" + "=" * 60)
    print("СТАТИСТИКА:")
    print(f"  Всего файлов: {stats['total']} ({len(html_files)})")
    print(f"  Изменено: {stats['modified']} ({stats['modified'] / stats['total'] * 100:.2f}%)")
    print(f"  Без изменений: {stats['unchanged']} ({stats['unchanged'] / stats['total'] * 100:.2f}%)")
    print(f"  Ошибок: {stats['errors']} ({stats['errors'] / stats['total'] * 100:.2f}%)")
    print("=" * 60)

    logger.info("Статистика завершения:")
    logger.info(f"  Всего файлов: {stats['total']} ({len(html_files)})")
    logger.info(f"  Изменено: {stats['modified']} ({stats['modified'] / stats['total'] * 100:.2f}%)")
    logger.info(f"  Без изменений: {stats['unchanged']} ({stats['unchanged'] / stats['total'] * 100:.2f}%)")
    logger.info(f"  Ошибок: {stats['errors']} ({stats['errors'] / stats['total'] * 100:.2f}%)") 

if __name__ == "__main__":
    main()