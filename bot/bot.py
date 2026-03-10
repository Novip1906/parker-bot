import sys
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from openai import AsyncOpenAI

# Добавляем корень проекта в путь для импорта config.py
root_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(root_dir)
import config

# Настройки бота берем из config
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
AI_API_KEY = config.AI_API_KEY
AI_MODEL_NAME = config.BOT_MODEL_NAME
BASE_URL = config.AI_BASE_URL
PROMPT_FILE = str(config.get_bot_prompt_path())

# Инициализация логирования
logger = config.setup_logging("bot")

if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в .env файле")
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

if not AI_API_KEY:
    logger.error("API ключ AI_PROVIDER_API_KEY не найден в .env файле")
    raise ValueError("API ключ AI_PROVIDER_API_KEY не найден в .env файле")

def get_system_prompt():
    try:
        if not os.path.exists(PROMPT_FILE):
             logger.warning(f"Файл промпта {PROMPT_FILE} не найден. Используется значение по умолчанию.")
             return "Ты — полезный AI-ассистент."
        with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Ошибка при чтении файла с промптом ({PROMPT_FILE}): {e}")
        return "Ты — полезный AI-ассистент."

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
openai_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=AI_API_KEY,
)

@dp.message(Command("start"))
async def start_handler(message: Message):
    logger.info(f"Команда /start от пользователя {message.from_user.id}")
    await message.answer(
        "Привет! Напиши мне любой текст, а я обработаю его и отправлю ответ."
    )

@dp.message()
async def handle_message(message: Message):
    # Пытаемся получить текст из обычного сообщения или подписи к медиафайлу
    user_text = message.text or message.caption
    if not user_text:
        return

    logger.info(f"Получено сообщение от {message.from_user.id}: {user_text[:50]}...")

    # Ограничение на 100 слов
    words = user_text.split()
    if len(words) > config.MAX_INPUT_WORDS:
        logger.warning(f"Сообщение от {message.from_user.id} слишком длинное ({len(words)} слов)")
        await message.answer(f"⚠️ Текст слишком длинный ({len(words)} слов). Пожалуйста, пришлите текст не более {config.MAX_INPUT_WORDS} слов.")
        return
    
    processing_msg = await message.answer("⏳ Анализирую текст...")
    
    system_prompt = get_system_prompt()
    
    try:
        logger.info(f"Отправка запроса в AI API (модель: {AI_MODEL_NAME})")
        response = await openai_client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=config.DEFAULT_TEMPERATURE
        )
        answer = response.choices[0].message.content
        usage = response.usage
        logger.info(f"Ответ от AI API получен успешно. Токены: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
        
        # Разбиваем длинные сообщения, если они превышают лимит Telegram (4096 символов)
        if len(answer) > 4000:
            logger.info("Ответ слишком длинный, разбиваем на части")
            parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
            await processing_msg.edit_text(parts[0])
            for part in parts[1:]:
                await message.answer(part)
        else:
            await processing_msg.edit_text(answer)
            
    except Exception as e:
        logger.error(f"API Error: {e}")
        await processing_msg.edit_text(f"❌ Произошла ошибка при обращении к API LLM.")

async def main():
    logger.info(f"🤖 Бот запущен. Используемый файл промпта: {PROMPT_FILE}")
    logger.info("Нажмите Ctrl+C для остановки.")
    
    # Удаляем вебхук и пропускаем накопившиеся сообщения
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
