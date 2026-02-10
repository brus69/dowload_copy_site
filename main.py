import subprocess

def faq_messge():
    # приветственное сообщение с функциональностью скрипта
    message_start = "Выберите сценарий работы:" \
    "\n 1) Отзеркалить сайт \n 2) Обработать html файлы пример: " \
    "было <div><div> стало <div> </div>  \n 3) Удалить js с кода страниц html" \
    "\n 4) Удалить js в линках \n 5) Удалить часть кода \n 6) Удалить часть текста" \
    "\n 7) Заменить часть кода \n 8) Добавить часть кода за тегом \n" \
    "Асинхронный режимы" \
    "2) "
    print(message_start)
    num = input()
    return num

def dowload_site(domain):
    # парсинг сайта через wget
    subprocess.run(['./download_site.sh', domain])
    return domain

def process_selection(num: str):
    # выбор функции в зависимости от значения
    if num == "1": 
        domain = input('Введите название домена')
        dowload_site(domain)
    elif num == "2":
        subprocess.run(['python3', 'recursive_html_processor.py'])
    elif num == "3":
        subprocess.run(['python3', 'remove_script.py'])
    elif num == '4':
        subprocess.run(['python3', 'remove_js_links.py'])
    elif num == '5':
        subprocess.run(['python3', 'remove_html_parts.py'])
    elif num == '6':
        dir_folder = input('Введите название директории ')
        clean_text = input('Текст к удалению ')
        subprocess.run(['./remove_text.sh', dir_folder, clean_text])
    elif num == '7':
        subprocess.run(['python3', 'replace_code.py'])
    elif num == '8':
        subprocess.run(['python3', 'append_code.py'])
    





def main():
    num = faq_messge()
    print('Выбор', num)
    process_selection(num)


if __name__ == '__main__':
    main()