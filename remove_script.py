import os
import re

def remove_script_tags(directory):
    """
    Находит все HTML-файлы в указанной директории и её поддиректориях,
    удаляет все <script>...</script> теги и их содержимое.

    :param directory: Путь к корневой папке для поиска файлов.
    """
    # Регулярное выражение для поиска <script>...</script> тегов
    script_pattern = re.compile(r'<script\b[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)

    # Рекурсивный обход всех файлов и папок
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Чтение содержимого файла
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Удаление <script>...</script> тегов
                    updated_content, count = script_pattern.subn('', content)

                    if count > 0:
                        # Сохранение изменений в файл
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                        print(f"Удалено {count} <script> тегов из файла: {file_path}")
                    else:
                        print(f"<script> теги не найдены в файле: {file_path}")

                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")


# Пример использования
if __name__ == "__main__":
    # Укажите путь к папке для поиска файлов
    target_directory = input('Укажите путь к папке для поиска файлов')

    # Вызов функции
    remove_script_tags(target_directory)