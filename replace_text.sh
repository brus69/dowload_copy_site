#!/bin/bash

if [[ $# -ne 3 ]]; then
    echo "Использование: $0 <каталог> <текст_для_поиска> <текст_для_замены>"
    exit 1
fi

DIRECTORY=$1
OLD_TEXT=$2
NEW_TEXT=$3
LOGFILE="replace.log"

# Проверяем, существует ли указанный каталог
if [[ ! -d "$DIRECTORY" ]]; then
    echo "Ошибка: Каталог $DIRECTORY не найден." | tee -a "$LOGFILE"
    exit 1
fi

# Находим все HTML файлы в указанном каталоге (рекурсивно)
HTML_FILES=$(find "$DIRECTORY" -type f -name "*.html")

if [[ -z "$HTML_FILES" ]]; then
    echo "$(date): В каталоге $DIRECTORY не найдено HTML файлов." | tee -a "$LOGFILE"
    exit 0
fi

# Флаг для проверки, были ли выполнены замены
REPLACEMENTS_MADE=false

# Проходим по каждому найденному HTML файлу
for FILE in $HTML_FILES; do
    if grep -q "$OLD_TEXT" "$FILE"; then
        sed -i "s/$OLD_TEXT/$NEW_TEXT/g" "$FILE"
        if [[ $? -eq 0 ]]; then
            echo "$(date): Замена '$OLD_TEXT' на '$NEW_TEXT' успешно выполнена в файле $FILE." | tee -a "$LOGFILE"
            REPLACEMENTS_MADE=true
        else
            echo "$(date): Ошибка при выполнении замены в файле $FILE." | tee -a "$LOGFILE"
        fi
    else
        echo "$(date): Текст '$OLD_TEXT' не найден в файле $FILE. Замена не выполнена." | tee -a "$LOGFILE"
    fi
done

# Если замены не были выполнены ни в одном файле
if [[ "$REPLACEMENTS_MADE" = false ]]; then
    echo "$(date): Текст '$OLD_TEXT' не был найден ни в одном из HTML файлов в каталоге $DIRECTORY." | tee -a "$LOGFILE"
    exit 0
fi
