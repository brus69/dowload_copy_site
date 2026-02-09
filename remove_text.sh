#!/bin/bash

# Проверка количества аргументов
if [[ $# -ne 2 ]]; then
    echo "Использование: $0 <директория> <текст_для_удаления>"
    exit 1
fi

# Настройки
DIRECTORY=$1                # Директория для поиска файлов
TEXT_TO_REMOVE=$2           # Текст для удаления
LOG_DIR="logs"              # Папка для хранения логов
LOGFILE="$LOG_DIR/remove_text.log" # Файл для логирования

# Создание папки logs, если она не существует
if [[ ! -d "$LOG_DIR" ]]; then
    mkdir -p "$LOG_DIR"
    if [[ $? -ne 0 ]]; then
        echo "Ошибка: Не удалось создать папку $LOG_DIR."
        exit 1
    fi
fi

# Проверка существования директории
if [[ ! -d "$DIRECTORY" ]]; then
    echo "Ошибка: Директория $DIRECTORY не найдена." | tee -a "$LOGFILE"
    exit 1
fi

# Поиск всех HTML-файлов в указанной директории и поддиректориях
HTML_FILES=$(find "$DIRECTORY" -type f -name "*.html")

# Если HTML-файлы не найдены
if [[ -z "$HTML_FILES" ]]; then
    echo "$(date): В директории $DIRECTORY не найдено ни одного HTML-файла." | tee -a "$LOGFILE"
    exit 0
fi

# Обработка каждого файла
for FILE in $HTML_FILES; do
    if grep -q "$TEXT_TO_REMOVE" "$FILE"; then
        # Удаление текста
        sed -i "/$TEXT_TO_REMOVE/d" "$FILE"
        if [[ $? -eq 0 ]]; then
            echo "$(date): Текст '$TEXT_TO_REMOVE' успешно удален из файла $FILE." | tee -a "$LOGFILE"
        else
            echo "$(date): Ошибка при удалении текста из файла $FILE." | tee -a "$LOGFILE"
        fi
    else
        echo "$(date): Текст '$TEXT_TO_REMOVE' не найден в файле $FILE. Удаление не выполнено." | tee -a "$LOGFILE"
    fi
done