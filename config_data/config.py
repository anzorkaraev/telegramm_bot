import os

from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings
from pydantic import SecretStr, StrictStr

if not find_dotenv():
    exit("Переменные окружения не загружены, так как отсутствует файл .env")
else:
    load_dotenv()


class SiteSettings(BaseSettings):
    bot_token: SecretStr = os.getenv("BOT_TOKEN", None)
    avia_token: SecretStr = os.getenv("AVIA_TOKEN", None)
    api_key: SecretStr = os.getenv("API_KEY", None)
    weather_key: SecretStr = os.getenv("WEATHER_KEY", None)


DEFAULT_COMMANDS = (
    ("start", "Запуск бота"),
    ("help", "Информация о боте"),
    ("low", "Самые дешевые билеты"),
    ("high", "Самые дорогие билеты"),
    ("custom", "Цены в выбранном диапазоне"),
    ("history", "История запросов")
)
