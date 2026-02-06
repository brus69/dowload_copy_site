import os
import re

# Настройки
FILES_DIR = "ecodpo.ru"  # Директория с HTML-файлами
HTML_PARTS_TO_REMOVE_FILE = "parts_to_remove.txt"  # Файл с частями HTML для удаления
LOGFILE = "remove.log"  # Файл для логирования

# Чтение частей HTML для удаления из файла
def read_html_parts_to_remove(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден.")
        exit(1)
    with open(file_path, "r", encoding="utf-8") as file:
        parts = file.read().split("-----")
    return [part.strip() for part in parts if part.strip()]

# Удаление частей HTML из файла
def remove_html_parts_from_file(file_path, parts_to_remove):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        original_content = content
        for part in parts_to_remove:
            # Экранирование специальных символов для использования в регулярных выражениях
            escaped_part = re.escape(part)
            content = re.sub(escaped_part, "", content, flags=re.DOTALL)
        
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return True
        return False
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return False

# Логирование
def log_message(message):
    with open(LOGFILE, "a", encoding="utf-8") as log:
        log.write(f"{message}\n")

# Основная функция
def main():
    # Чтение частей HTML для удаления
    parts_to_remove = read_html_parts_to_remove(HTML_PARTS_TO_REMOVE_FILE)
    if not parts_to_remove:
        print("Ошибка: Нет частей HTML для удаления.")
        exit(1)

    # Обработка всех HTML-файлов в директории
    for root, _, files in os.walk(FILES_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                if remove_html_parts_from_file(file_path, parts_to_remove):
                    log_message(f"Удалены части HTML из файла: {file_path}")
                else:
                    log_message(f"Части HTML не найдены в файле: {file_path}")

    print("Обработка завершена. Проверьте логи в файле remove.log.")

if __name__ == "__main__":
    main()
