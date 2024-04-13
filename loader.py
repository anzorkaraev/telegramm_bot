from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_data.config import SiteSettings


data = SiteSettings()

storage = StateMemoryStorage()
bot = TeleBot(token=data.bot_token.get_secret_value(), state_storage=storage)
