#!/usr/bin/env python3
"""
Скрипт для рекурсивного добавления нового фрагмента кода после целевого участка в HTML файлах
"""

import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Для отображения прогресс-бара
import logging

# Настройка логгера
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # Создаем директорию logs, если её нет
LOG_FILE = LOG_DIR / "append_code_after_html_snippet.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)

logger = logging.getLogger("code_appender")


def append_code_in_file(file_path, target_code, new_code):
    """
    Добавляет новый фрагмент кода после целевого участка в указанном файле.

    :param file_path: Путь к файлу.
    :param target_code: Участок кода, после которого нужно добавить новый фрагмент.
    :param new_code: Новый фрагмент кода или текста для добавления.
    :return: True, если файл был изменён, иначе False.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        if target_code in content:
            updated_content = content.replace(target_code, target_code + new_code)
            file_path.write_text(updated_content, encoding="utf-8")
            logger.info(f"Обновлен файл: {file_path}")
            return True
        else:
            logger.info(f"Целевой код не найден в файле: {file_path}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        return False


def main():
    print('Добавление нового фрагмента кода в HTML файлы\n')
    
    # Ввод пути к директории
    target_directory = Path(input('Укажите путь к папке для поиска файлов: ').strip())
    
    # Участок кода, после которого нужно добавить новый фрагмент
    target_code_snippet = input('Участок кода, после которого нужно добавить новый фрагмент: ').strip()
    
    # Новый фрагмент кода или текста для добавления
    new_code_snippet = input('Новый фрагмент кода или текста для добавления: ').strip()

    print("=" * 60)
    print("Добавление нового фрагмента кода в HTML файлы")
    print(f"Директория: {target_directory}")
    print("=" * 60)

    # Проверяем существование директории
    if not target_directory.exists():
        logger.error(f"Ошибка: Директория {target_directory} не существует!")
        return

    # Находим все HTML файлы
    html_files = list(target_directory.rglob('*.html'))  # Рекурсивный поиск

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
            executor.submit(append_code_in_file, file, target_code_snippet, new_code_snippet): file
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