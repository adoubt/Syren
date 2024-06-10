from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


token="7167825365:AAEQhLkT88eAnJa_a5IcvH1FfnMyD32QEWk"
MANIFEST_URL = 'MANIFEST_URL'
super_admin = "6279510886"
password = '1234' # /set_admin{password}


bot_id = token.split(":",1)[0]
bot = Bot(token)
dp = Dispatcher(storage=MemoryStorage())


#AAIO   
aaio_token = 'xxxxx'
merchant_id = 'xxxxx' # ID магазина
secret = 'xxxxx' # Секретный ключ №1 из настроек магазина
secret2 = 'xxxxx' # Секретный ключ №2 из настроек магазина