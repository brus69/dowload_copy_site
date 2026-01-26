#!/bin/bash

# Проверка количества аргументов
if [[ $# -ne 2 ]]; then
    echo "Использование: $0 <файл> <текст_для_удаления>"
    exit 1
fi

# Настройки
FILE=$1                      # Файл, в котором выполняется удаление
TEXT_TO_REMOVE=$2            # Текст для удаления
LOGFILE="remove.log"         # Файл для логирования

# Проверка существования файла
if [[ ! -f "$FILE" ]]; then
    echo "Ошибка: Файл $FILE не найден." | tee -a "$LOGFILE"
    exit 1
fi

# Создание резервной копии файла (опционально)
cp "$FILE" "${FILE}.bak"

# Проверка наличия текста в файле
if grep -q "$TEXT_TO_REMOVE" "$FILE"; then
    # Удаление текста
    sed -i "/$TEXT_TO_REMOVE/d" "$FILE"
    if [[ $? -eq 0 ]]; then
        echo "$(date): Текст '$TEXT_TO_REMOVE' успешно удален из файла $FILE." | tee -a "$LOGFILE"
    else
        echo "$(date): Ошибка при удалении текста из файла $FILE." | tee -a "$LOGFILE"
        exit 1
    fi
else
    echo "$(date): Текст '$TEXT_TO_REMOVE' не найден в файле $FILE. Удаление не выполнено." | tee -a "$LOGFILE"
    exit 0
fi
