import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения из .env в корне проекта
root_dir = os.path.join(os.path.dirname(__file__), '..')
load_dotenv(os.path.join(root_dir, '.env'))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

AI_API_KEY = os.getenv("AI_PROVIDER_API_KEY") 
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "google/gemini-2.5-flash")


if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

if not AI_API_KEY:
    raise ValueError("API ключ AI_PROVIDER_API_KEY не найден в .env файле")

BASE_URL = os.getenv("AI_PROVIDER_BASE_URL", "https://polza.ai/api/v1")

# Устанавливаем пути к файлу с промптом
PROMPT_FILE = "prompt.txt"
if not os.path.exists(PROMPT_FILE):
    # Если локального нет, берем сгенерированный из model-training
    PROMPT_FILE = os.path.join(root_dir, 'model-training', 'prompt.txt')

def get_system_prompt():
    try:
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Ошибка при чтении файла с промптом ({PROMPT_FILE}): {e}")
        return "Ты — полезный AI-ассистент."

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
openai_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=AI_API_KEY,
)

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Привет! Напиши мне любой текст, а я обработаю его и отправлю ответ."
    )

@dp.message()
async def handle_message(message: Message):
    user_text = message.text
    if not user_text:
        return

    # Ограничение на 100 слов
    words = user_text.split()
    if len(words) > 100:
        await message.answer(f"⚠️ Текст слишком длинный ({len(words)} слов). Пожалуйста, пришлите текст не более 100 слов.")
        return
    
    processing_msg = await message.answer("⏳ Анализирую текст...")
    
    system_prompt = get_system_prompt()
    
    try:
        response = await openai_client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content
        
        # Разбиваем длинные сообщения, если они превышают лимит Telegram (4096 символов)
        if len(answer) > 4000:
            parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
            await processing_msg.edit_text(parts[0])
            for part in parts[1:]:
                await message.answer(part)
        else:
            await processing_msg.edit_text(answer)
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ Произошла ошибка при обращении к API LLM.")
        print(f"API Error: {e}")

async def main():
    print(f"🤖 Бот запущен. Используемый файл промпта: {os.path.relpath(PROMPT_FILE, start=root_dir)}")
    print("Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
