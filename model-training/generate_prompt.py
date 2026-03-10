import sys
import os
import openai

# Добавляем корень проекта в путь для импорта config.py
root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(root_dir)
import config

def get_openai_response(system_content, user_content):
    try:
        print("Отправка запроса в API...")
        
        client = openai.OpenAI(
            base_url=config.AI_BASE_URL,
            api_key=config.AI_API_KEY,
        )

        model_name = config.TRAINING_MODEL_NAME
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        )

        print("Ответ получен.")

        return response.choices[0].message.content
            
    except Exception as e:
        print(f"Произошла ошибка при запросе: {e}")
        return None

def save_response_to_txt(content, file_path="data/response.txt"):
    """
    Сохраняет контент в .txt файл.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Ответ успешно сохранен в: {file_path}")
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Загружаем шаблон промпта
    meta_prompt_path = config.META_PROMPT_PATH
    if not meta_prompt_path.exists():
        print(f"Ошибка: Файл {meta_prompt_path} не найден.")
        exit(1)
        
    with open(meta_prompt_path, "r", encoding="utf-8") as f:
        meta_prompt_template = f.read()

    # 2. Загружаем посты (возьмем первые N штук для анализа из config)
    data_path = config.CLEANED_DATA_PATH
    if not data_path.exists():
        print(f"Ошибка: Файл {data_path} не найден. Сначала запустите clean_data.py")
        exit(1)

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            # Читаем все строки и берем первые посты из конфига
            all_posts = [line.strip() for line in f if line.strip()]
            posts_to_analyze = all_posts[:config.TRAINING_POSTS_COUNT]
            # Форматируем их списком для промпта
            posts_formatted = "\n\n".join([post for post in posts_to_analyze])
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        exit(1)

    # 3. Формируем финальный запрос
    system_prompt = meta_prompt_template.format(posts_chunk=posts_formatted)
    
    if system_prompt:
        answer = get_openai_response(system_prompt, posts_formatted)
        if answer:
            # Путь к файлу для сохранения результата
            output_file = config.GENERATED_PROMPT_PATH
            save_response_to_txt(answer, output_file)
    else:
        print("Не удалось сформировать запрос.")


