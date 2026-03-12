import sys
import os
import openai

root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(root_dir)
import config

logger = config.setup_logging("generate_prompt")

def get_openai_response(system_content, user_content):
    try:
        logger.info("Отправка запроса в API...")
        
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

        usage = response.usage
        logger.info(f"Ответ от API получен. Токены: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")

        return response.choices[0].message.content
            
    except Exception as e:
        logger.error(f"Произошла ошибка при запросе к API: {e}")
        return None

def save_response_to_txt(content, file_path="data/response.txt"):
    """
    Сохраняет контент в .txt файл.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Ответ успешно сохранен в: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла {file_path}: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    meta_prompt_path = config.META_PROMPT_PATH
    if not meta_prompt_path.exists():
        logger.error(f"Файл {meta_prompt_path} не найден.")
        exit(1)
        
    try:
        with open(meta_prompt_path, "r", encoding="utf-8") as f:
            meta_prompt_template = f.read()
    except Exception as e:
        logger.error(f"Ошибка при чтении {meta_prompt_path}: {e}")
        exit(1)

    data_path = config.CLEANED_DATA_PATH
    if not data_path.exists():
        logger.error(f"Файл {data_path} не найден. Сначала запустите clean_data.py")
        exit(1)

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            all_posts = [line.strip() for line in f if line.strip()]
            posts_to_analyze = all_posts[:config.TRAINING_POSTS_COUNT]
            logger.info(f"Загружено {len(posts_to_analyze)} постов для анализа")
            posts_formatted = "\n\n".join([post for post in posts_to_analyze])
    except Exception as e:
        logger.error(f"Ошибка при чтении данных {data_path}: {e}")
        exit(1)

    try:
        system_prompt = meta_prompt_template.format(posts_chunk=posts_formatted)
        
        if system_prompt:
            answer = get_openai_response(system_prompt, posts_formatted)
            if answer:
                output_file = config.GENERATED_PROMPT_PATH
                save_response_to_txt(answer, output_file)
        else:
            logger.error("Не удалось сформировать запрос (пустой системный промпт).")
    except Exception as e:
        logger.error(f"Ошибка при формировании или отправке запроса: {e}")
