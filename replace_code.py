import os

def replace_code_in_html_files(directory, old_code, new_code):
    """
    Находит все HTML-файлы в указанной директории и её поддиректориях,
    заменяет заданный участок кода на новый и сохраняет изменения.

    :param directory: Путь к корневой папке для поиска файлов.
    :param old_code: Участок кода, который нужно заменить.
    :param new_code: Новый участок кода для замены.
    """
    # Рекурсивный обход всех файлов и папок
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # Чтение содержимого файла
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Проверка наличия старого кода
                    if old_code in content:
                        # Замена старого кода на новый
                        updated_content = content.replace(old_code, new_code)

                        # Сохранение изменений в файл
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                        print(f"Обновлен файл: {file_path}")
                    else:
                        print(f"Старый код не найден в файле: {file_path}")

                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")


# Пример использования
if __name__ == "__main__":
    # Укажите путь к папке для поиска файлов
    target_directory = input('Укажите путь к папке для поиска файлов ')

    # Участок кода/текста, который нужно заменить
    old_code_snippet = input('Участок кода/текста, который нужно заменить ')

    # Новый участок кода
    new_code_snippet = input('Новый участок кода ')

    # Вызов функции
    replace_code_in_html_files(target_directory, old_code_snippet, new_code_snippet)