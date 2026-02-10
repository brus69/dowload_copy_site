import os
import xml.etree.ElementTree as ET

# Функция для рекурсивного поиска HTML-файлов
def find_html_files(base_path):
    html_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".html"):
                # Формируем относительный путь к файлу
                relative_path = os.path.relpath(os.path.join(root, file), base_path)
                html_files.append(relative_path)
    return html_files

# Функция для создания sitemap.xml
def generate_sitemap(base_url, base_path):
    # Получаем список HTML-файлов
    html_files = find_html_files(base_path)
    
    # Создаем корневой элемент <urlset>
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Добавляем URL-адреса
    for file in html_files:
        # Преобразуем путь файла в URL (заменяем обратные слеши на прямые и убираем расширение .html)
        url_path = file.replace("\\", "/").replace(".html", "")
        full_url = f"{base_url.rstrip('/')}/{url_path}"
        
        url_element = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_element, "loc")
        loc.text = full_url
    
    # Создаем дерево XML
    tree = ET.ElementTree(urlset)
    
    # Записываем результат в файл
    with open("sitemap.xml", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)

# Параметры
base_url = "https://example.com"  # Базовый URL вашего сайта
base_path = "./ecodpo.ru"       # Локальная папка, куда скачаны файлы

# Генерация sitemap.xml
generate_sitemap(base_url, base_path)

print("Sitemap успешно создан!")