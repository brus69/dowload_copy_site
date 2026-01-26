#!/bin/bash

if [[ $# -ne 3 ]]; then
    echo "Использование: $0 <файл> <текст_для_поиска> <текст_для_замены>"
    exit 1
fi

FILE=$1
OLD_TEXT=$2
NEW_TEXT=$3
LOGFILE="replace.log"

if [[ ! -f "$FILE" ]]; then
    echo "Ошибка: Файл $FILE не найден." | tee -a "$LOGFILE"
    exit 1
fi

if grep -q "$OLD_TEXT" "$FILE"; then
    sed -i "s/$OLD_TEXT/$NEW_TEXT/g" "$FILE"
    if [[ $? -eq 0 ]]; then
        echo "$(date): Замена '$OLD_TEXT' на '$NEW_TEXT' успешно выполнена в файле $FILE." | tee -a "$LOGFILE"
    else
        echo "$(date): Ошибка при выполнении замены в файле $FILE." | tee -a "$LOGFILE"
        exit 1
    fi
else
    echo "$(date): Текст '$OLD_TEXT' не найден в файле $FILE. Замена не выполнена." | tee -a "$LOGFILE"
    exit 0
fi
