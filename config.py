import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.resolve()

load_dotenv(ROOT_DIR / ".env")

# --- API и Ключи ---
AI_API_KEY = os.getenv("AI_PROVIDER_API_KEY")
AI_BASE_URL = os.getenv("AI_PROVIDER_BASE_URL", "https://polza.ai/api/v1")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Модели ---
# Модель для работы бота в Telegram
BOT_MODEL_NAME = os.getenv("AI_MODEL_NAME", "google/gemini-2.5-flash")
# Модель для генерации системного промпта (обучения)
TRAINING_MODEL_NAME = os.getenv("MODEL_TRAINING_MODEL_NAME", "google/gemini-2.5-pro")

# --- Настройки генерации и обработки ---
# Настройки для бота
DEFAULT_TEMPERATURE = 0.7
MAX_INPUT_WORDS = 100  # Максимальное количество слов от пользователя

# Настройки для обучения/анализа данных
TRAINING_POSTS_COUNT = 100  # Количество постов для анализа при генерации промпта
MIN_WORDS_FOR_CLEANING = 5   # Минимальное количество слов в посте для обучения
MAX_WORDS_FOR_CLEANING = 100 # Максимальное количество слов в посте для обучения

# --- Пути к файлам ---
MODEL_TRAINING_DIR = ROOT_DIR / "model-training"
DATA_DIR = MODEL_TRAINING_DIR / "data"

# Файлы данных
RAW_DATA_PATH = MODEL_TRAINING_DIR / "raw_data.json"
CLEANED_DATA_PATH = DATA_DIR / "cleaned_data.txt"
META_PROMPT_PATH = DATA_DIR / "meta_prompt.txt"

# Результирующий промпт
# Бот сначала ищет промпт у себя в папке, если нет - берет из папки обучения
BOT_PROMPT_LOCAL = ROOT_DIR / "bot" / "prompt.txt"
GENERATED_PROMPT_PATH = MODEL_TRAINING_DIR / "prompt.txt"

def get_bot_prompt_path():
    """Возвращает путь к актуальному файлу промпта."""
    if BOT_PROMPT_LOCAL.exists():
        return BOT_PROMPT_LOCAL
    return GENERATED_PROMPT_PATH

def setup_logging(name):
    """Настраивает и возвращает логгер."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger(name)
