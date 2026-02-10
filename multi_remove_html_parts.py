#!/usr/bin/env python3
"""
Скрипт для рекурсивного удаления частей HTML из файлов на основе содержимого файла parts_to_remove.txt
"""

import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Для отображения прогресс-бара
import logging

# Настройка логгера
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # Создаем директорию logs, если её нет
LOG_FILE = LOG_DIR / "remove_html_parts.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)

logger = logging.getLogger("html_part_remover")

# Чтение частей HTML для удаления из файла
def read_html_parts_to_remove(file_path):
    """
    Читает части HTML для удаления из файла.

    :param file_path: Путь к файлу с частями HTML для удаления.
    :return: Список частей HTML для удаления.
    """
    if not file_path.exists():
        logger.error(f"Ошибка: Файл {file_path} не найден.")
        exit(1)
    
    with file_path.open("r", encoding="utf-8") as file:
        parts = file.read().split("-----")
    
    return [part.strip() for part in parts if part.strip()]


def remove_html_parts_from_file(file_path, patterns):
    """
    Удаляет указанные части HTML из файла.

    :param file_path: Путь к файлу.
    :param patterns: Список предварительно скомпилированных регулярных выражений.
    :return: True, если файл был изменён, иначе False.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        original_content = content
        
        for pattern in patterns:
            content = pattern.sub("", content)
        
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Удалены части HTML из файла: {file_path}")
            return True
        else:
            logger.info(f"Части HTML не найдены в файле: {file_path}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        return False


def main():
    print('Важно! Должен быть файл parts_to_remove.txt и в нём код HTML для удаления\n')
    
    # Ввод пути к директории
    files_dir = Path(input('Выберите директорию с HTML-файлами: ').strip())
    html_parts_to_remove_file = Path("parts_to_remove.txt")  # Файл с частями HTML для удаления

    print("=" * 60)
    print("Удаление частей HTML из файлов")
    print(f"Директория: {files_dir}")
    print("=" * 60)

    # Чтение частей HTML для удаления
    parts_to_remove = read_html_parts_to_remove(html_parts_to_remove_file)
    if not parts_to_remove:
        logger.error("Ошибка: Нет частей HTML для удаления.")
        exit(1)

    # Компиляция регулярных выражений заранее
    compiled_patterns = [re.compile(re.escape(part), flags=re.DOTALL) for part in parts_to_remove]

    # Находим все HTML файлы
    html_files = list(files_dir.rglob('*.html'))  # Рекурсивный поиск

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

    # Многопоточная обработка с прогресс-баром
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(remove_html_parts_from_file, file, compiled_patterns): file
            for file in html_files
        }

        # Отображаем прогресс
        for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка файлов", unit="файл"):
            file = futures[future]
            try:
                modified = future.result()
                if modified:
                    stats['modified'] += 1
                else:
                    stats['unchanged'] += 1
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Неожиданная ошибка при обработке файла {file}: {e}")

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