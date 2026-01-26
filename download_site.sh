#!/bin/bash

# Проверка количества аргументов
if [[ $# -ne 1 ]]; then
    echo "Использование: $0 <домен>"
    echo "Пример: $0 themashina.ru"
    exit 1
fi

# Настройки
DOMAIN=$1                     # Доменное имя (например, themashina.ru)
BASE_DIR="$DOMAIN"           # Папка для сохранения сайта
LOGFILE="wget_$DOMAIN.log"   # Файл для логирования

# Проверка, что домен не пустой
if [[ -z "$DOMAIN" ]]; then
    echo "Ошибка: Доменное имя не должно быть пустым."
    exit 1
fi

# Удаляем протокол из домена, если он есть
DOMAIN="${DOMAIN#https://}"
DOMAIN="${DOMAIN#http://}"
DOMAIN="${DOMAIN#www.}"

echo "========================================"
echo "Загрузка сайта: $DOMAIN"
echo "Лог-файл: $LOGFILE"
echo "Папка сохранения: $BASE_DIR"
echo "========================================"

# Проверяем, существует ли уже папка с таким именем
if [[ -d "$BASE_DIR" ]]; then
    echo "Внимание: Папка '$BASE_DIR' уже существует!"
    read -p "Удалить существующую папку? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$BASE_DIR"
        echo "Старая папка удалена."
    else
        echo "Отмена загрузки."
        exit 1
    fi
fi

# Загрузка сайта с помощью wget
echo "Начинаем загрузку сайта $DOMAIN..."
echo "Это может занять некоторое время..."

wget \
    --no-check-certificate \
    --recursive \
    --page-requisites \
    --html-extension \
    --convert-links \
    --restrict-file-names=unix \
    --domains="$DOMAIN" \
    --no-parent \
    --reject="index.php*" \
    --cut-dirs=1 \
    --timeout=30 \
    --tries=3 \
    --wait=2 \
    --random-wait \
    --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    --progress=bar:force:noscroll \
    --directory-prefix="$BASE_DIR" \
    --output-file="$LOGFILE" \
    "https://$DOMAIN"

# Проверка завершения
if [[ $? -eq 0 ]]; then
    echo "========================================"
    echo "Загрузка завершена успешно!"
    echo "Копия сайта сохранена в директории: $BASE_DIR"
    echo "Логи сохранены в файле: $LOGFILE"
    echo "========================================"
    
    # Показываем статистику
    echo "Статистика:"
    echo "Количество HTML файлов: $(find "$BASE_DIR" -name "*.html" -o -name "*.htm" | wc -l)"
    echo "Количество CSS файлов: $(find "$BASE_DIR" -name "*.css" | wc -l)"
    echo "Количество JS файлов: $(find "$BASE_DIR" -name "*.js" | wc -l)"
    echo "Количество изображений: $(find "$BASE_DIR" -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.gif" -o -name "*.svg" | wc -l)"
    echo "Общий размер: $(du -sh "$BASE_DIR" | cut -f1)"
    
    # Показываем последние строки лога
    echo ""
    echo "Последние строки лога:"
    tail -10 "$LOGFILE"
else
    echo "========================================"
    echo "Ошибка при загрузке сайта!"
    echo "Проверьте логи в файле: $LOGFILE"
    echo "Последние ошибки:"
    tail -20 "$LOGFILE" | grep -i "error\|failed\|warning"
    echo "========================================"
    exit 1
fi
