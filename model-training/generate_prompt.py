import os
import openai
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройка API ключа
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_response(prompt):
    try:
        print("Отправка запроса в OpenAI...")
        
        client = openai.OpenAI(
            base_url=os.getenv("AI_PROVIDER_BASE_URL", "https://polza.ai/api/v1"),
            api_key=os.getenv("AI_PROVIDER_API_KEY"),
        )

        model_name = os.getenv("MODEL_TRAINING_MODEL_NAME", "google/gemini-2.5-flash")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{
                "role": "user",
                "content": prompt
            }]
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
    meta_prompt_path = os.path.join(script_dir, "data/meta_prompt.txt")
    if not os.path.exists(meta_prompt_path):
        print(f"Ошибка: Файл {meta_prompt_path} не найден.")
        exit(1)
        
    with open(meta_prompt_path, "r", encoding="utf-8") as f:
        meta_prompt_template = f.read()

    # 2. Загружаем посты (возьмем первые 30 штук для анализа)
    data_path = os.path.join(script_dir, "data/cleaned_data.txt")
    if not os.path.exists(data_path):
        # Попробуем найти в текущей директории, если скрипт запущен из корня
        data_path = os.path.join(os.getcwd(), "model-training", "data/cleaned_data.txt")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            # Читаем все строки и берем первые 30 ненулевых
            all_posts = [line.strip() for line in f if line.strip()]
            posts_to_analyze = all_posts[:30]
            # Форматируем их списком для промпта
            posts_formatted = "\n\n".join([f"Пост {i+1}:\n{post}" for i, post in enumerate(posts_to_analyze)])
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")
        exit(1)

    # 3. Формируем финальный запрос
    user_request = meta_prompt_template.format(posts_chunk=posts_formatted)
    
    if user_request:
        answer = get_openai_response(user_request)
        if answer:
            # Путь к файлу для сохранения результата
            output_file = os.path.join(script_dir, "prompt.txt")
            save_response_to_txt(answer, output_file)
    else:
        print("Не удалось сформировать запрос.")


