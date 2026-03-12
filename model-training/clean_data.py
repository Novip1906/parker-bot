import json
import os
import re
import sys

root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(root_dir)
import config

logger = config.setup_logging("clean_data")

def is_valid_text(text):
    text_lower = text.lower()
    
    if '@' in text:
        return False
    
    if re.search(r'https?://\S+|www\.\S+', text):
        return False
    
    words = text.split()
    if len(words) <= config.MIN_WORDS_FOR_CLEANING or len(words) >= config.MAX_WORDS_FOR_CLEANING:
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
    input_file_path = config.RAW_DATA_PATH
    output_txt_path = config.CLEANED_DATA_PATH
    
    if not input_file_path.exists():
        logger.error(f"Файл {input_file_path} не найден.")
        return

    logger.info(f"Загрузка {input_file_path}...")
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Ошибка при загрузке JSON: {e}")
        return

    if isinstance(data, dict) and 'messages' in data:
        messages = data['messages']
        logger.info(f"Найдено сообщений: {len(messages)}")
        
        cleaned_messages = []
        for msg in messages:
            if 'text' in msg:
                text = extract_text(msg['text'])
                
                text = text.replace('\n', ' ')
                text = re.sub(r'\s+', ' ', text).strip()
                
                if is_valid_text(text):
                    cleaned_messages.append({'text': text})
        
        logger.info(f"Обработано и отфильтровано сообщений: {len(cleaned_messages)}")
            
        try:
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                for msg in cleaned_messages:
                    f.write(msg['text'] + '\n')
            logger.info(f"Файл успешно создан: {output_txt_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла: {e}")
    else:
        logger.error("Структура JSON не совпадает с ожидаемым экспортом Telegram.")

if __name__ == "__main__":
    clean_json()
