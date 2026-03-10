import json
import os
import re

def is_valid_text(text):
    text_lower = text.lower()
    
    # 1. Удаляем если есть @ (упоминания)
    if '@' in text:
        return False
    
    # 2. Удаляем если есть явные ссылки
    if re.search(r'https?://\S+|www\.\S+', text):
        return False
        
    # 3. Фильтр стоп-слов (реклама, призывы, каналы)
    stop_keywords = [
        'подпишитесь', 'подписывайтесь', 'канал', 'ссылке', 
        'реклама', 'переходите', 'заходите', 'читать далее',
        'в комментариях', 'подробности', 'инсайд', 'мерч'
    ]
    for word in stop_keywords:
        if word in text_lower:
            return False
    
    # 4. Проверка на количество слов (должно быть > 3)
    words = text.split()
    if len(words) <= 3:
        return False
    
    # 5. Проверка на наличие эмодзи
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010ffff" 
        "\u2600-\u27BF"         
        "]+", flags=re.UNICODE
    )
    if emoji_pattern.search(text):
        return False
        
    return True

def extract_text(text_val):
    if isinstance(text_val, str):
        return text_val
    if isinstance(text_val, list):
        result = []
        for part in text_val:
            if isinstance(part, str):
                result.append(part)
            elif isinstance(part, dict) and "text" in part:
                result.append(part["text"])
        return "".join(result)
    return ""

def clean_json():
    input_file_path = 'raw_data.json'
    output_json_path = 'cleaned_data.json'
    output_txt_path = 'cleaned_data.txt'
    
    if not os.path.exists(input_file_path):
        print(f"Файл {input_file_path} не найден.")
        return

    print(f"Загрузка {input_file_path}...")
    with open(input_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'messages' in data:
        messages = data['messages']
        print(f"Найдено сообщений: {len(messages)}")
        
        cleaned_messages = []
        for msg in messages:
            if 'text' in msg:
                # Извлекаем текст
                text = extract_text(msg['text'])
                
                # ЗАМЕНЯЕМ переносы строк на пробелы (как просили в новом запросе)
                text = text.replace('\n', ' ')
                # Убираем лишние пробелы по краям и двойные пробелы
                text = re.sub(r'\s+', ' ', text).strip()
                
                # Фильтруем сообщения по остальным правилам
                if is_valid_text(text):
                    cleaned_messages.append({'text': text})
        
        print(f"Обработано и отфильтровано сообщений: {len(cleaned_messages)}")
            
        # Сохраняем результат в TXT (каждое сообщение с новой строки)
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            for msg in cleaned_messages:
                f.write(msg['text'] + '\n')
        
        print(f"Файлы успешно созданы: {output_json_path} и {output_txt_path}")
    else:
        print("Структура JSON не совпадает с ожидаемым экспортом Telegram.")

if __name__ == "__main__":
    clean_json()
