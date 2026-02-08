import os
import re

print('Работа скрипта remove_js_links.py')

def remove_js_links(directory):
    """
    Находит все HTML-файлы в указанной директории и её поддиректориях,
    удаляет все <link> теги, где href заканчивается на .js.

    :param directory: Путь к корневой папке для поиска файлов.
    """
    # Регулярное выражение для поиска <link> тегов с href, заканчивающимся на .js
    link_pattern = re.compile(r'<link\b[^>]*href="[^"]*\.js"[^>]*>', re.IGNORECASE)

    # Рекурсивный обход всех файлов и папок
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Чтение содержимого файла
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Удаление <link> тегов с href, заканчивающимся на .js
                    updated_content, count = link_pattern.subn('', content)

                    if count > 0:
                        # Сохранение изменений в файл
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                        print(f"Удалено {count} <link> тегов из файла: {file_path}")
                    else:
                        print(f"<link> теги с href, заканчивающимся на .js, не найдены в файле: {file_path}")

                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")


# Пример использования
if __name__ == "__main__":
    # Укажите путь к папке для поиска файлов
    target_directory = "ecodpo.ru"

    # Вызов функции
    remove_js_links(target_directory)