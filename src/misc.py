from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN=os.getenv('BOT_TOKEN')
MANIFEST_URL =os.getenv('MANIFEST_URL')
SUPER_ADMIN = os.getenv('SUPER_ADMIN')
PASSWORD = os.getenv('PASSWORD') # /set_admin{PASSWORD}
SERVICE_FEE = float(os.getenv('SERVICE_FEE'))

bot_id = BOT_TOKEN.split(":",1)[0]
bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


#AAIO   
AAIO_TOKEN = os.getenv('AAIO_TOKEN')
MERCHANT_ID = os.getenv('MERCHANT_ID') # ID магазина
SECRET = os.getenv('SECRET') # Секретный ключ №1 из настроек магазина
SECRET2 = os.getenv('SECRET2') # Секретный ключ №2 из настроек магазина