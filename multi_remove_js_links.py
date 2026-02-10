#!/usr/bin/env python3
"""
Скрипт для рекурсивного удаления <link> тегов с href, заканчивающимся на .js, из HTML файлов
"""

import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm  # Для отображения прогресс-бара
import logging

# Настройка логгера
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)  # Создаем директорию logs, если её нет
LOG_FILE = LOG_DIR / "remove_js_links.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Логи в файл
        logging.StreamHandler()         # Логи в консоль
    ]
)

logger = logging.getLogger("js_link_remover")

# Компиляция регулярного выражения заранее
LINK_PATTERN = re.compile(r'<link\b[^>]*href="[^"]*\.js"[^>]*>', re.IGNORECASE)


def remove_js_links_from_file(file_path):
    """
    Удаляет <link> теги с href, заканчивающимся на .js, из указанного файла.

    :param file_path: Путь к файлу.
    :return: Количество удалённых тегов или None при ошибке.
    """
    try:
        # Чтение содержимого файла
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Удаление <link> тегов с href, заканчивающимся на .js
        updated_content, count = LINK_PATTERN.subn('', content)

        if count > 0:
            # Сохранение изменений в файл
            file_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Удалено {count} <link> тегов из файла: {file_path}")
        else:
            logger.info(f"<link> теги с href, заканчивающимся на .js, не найдены в файле: {file_path}")

        return count

    except Exception as e:
        logger.error(f"Ошибка при обработке файла {file_path}: {e}")
        return None


def main():
    print('Работа скрипта remove_js_links.py\n')

    # Ввод пути к директории
    target_directory = input("Укажите путь к папке для поиска файлов: ").strip()
    base_path = Path(target_directory)

    print("=" * 60)
    print("Удаление <link> тегов с href, заканчивающимся на .js, из HTML файлов")
    print(f"Директория: {target_directory}")
    print("=" * 60)

    # Проверяем существование директории
    if not base_path.exists():
        logger.error(f"Ошибка: Директория {target_directory} не существует!")
        return

    # Находим все HTML файлы
    html_files = list(base_path.rglob('*.html'))  # Рекурсивный поиск

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
            executor.submit(remove_js_links_from_file, file): file
            for file in html_files
        }

        # Отображаем прогресс
        for future in tqdm(as_completed(futures), total=len(futures), desc="Обработка файлов", unit="файл"):
            file = futures[future]
            try:
                count = future.result()
                if count is None:
                    stats['errors'] += 1
                elif count > 0:
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