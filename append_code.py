import os

def append_code_after_html_snippet(directory, target_code, new_code):
    """
    Находит все HTML-файлы в указанной директории и её поддиректориях,
    ищет заданный участок кода и добавляет после него новый фрагмент.

    :param directory: Путь к корневой папке для поиска файлов.
    :param target_code: Участок кода, после которого нужно добавить новый фрагмент.
    :param new_code: Новый фрагмент кода или текста для добавления.
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

                    # Проверка наличия целевого кода
                    if target_code in content:
                        # Добавление нового кода после целевого участка
                        updated_content = content.replace(target_code, target_code + new_code)

                        # Сохранение изменений в файл
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                        print(f"Обновлен файл: {file_path}")
                    else:
                        print(f"Целевой код не найден в файле: {file_path}")

                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")


# Пример использования
if __name__ == "__main__":
    # Укажите путь к папке для поиска файлов
    target_directory = input('Укажите путь к папке')

    # Участок кода, после которого нужно добавить новый фрагмент
    target_code_snippet = input('Участок кода, после которого нужно добавить новый фрагмент')
    # Новый фрагмент кода или текста для добавления
    new_code_snippet = input('Новый фрагмент кода или текста для добавления')

    # Вызов функции
    append_code_after_html_snippet(target_directory, target_code_snippet, new_code_snippet)