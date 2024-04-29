import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from loguru import logger

from src.keyboards import user_keyboards

from src.methods.database.users_manager import UsersDatabase
# from src.methods.database.payments_manager import OrdersDatabase
from src.methods.database.products_manager import ProductsDatabase
from src.methods.database.licenses_manager import LicensesDatabase
from src.methods.database.carts_manager import CartsDatabase
# from src.methods.payment import aaio_manager
# from src.methods.payment.payment_processing import ProcessOrder

router =  Router()
from src.misc import bot,bot_id, super_admin,password
from src.handlers.decorators import new_seller_handler, new_user_handler

@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False, **kwargs):

    text = 'ff' #start_msg
    
    if is_clb:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
    if message.text != "/start":
        data = message.text.split(" ",1)[-1]
        product_id = int(data)
        # mp3_link = await ProductsDatabase.get_value("mp3_link", product_id) 
        product = await ProductsDatabase.get_product(product_id)
        mp3_link = product[5]
        image_link = product[8]
        is_sold = product[9]
        collab = product[11]
        tags = product[12]
        feature = await LicensesDatabase.get_value("feature")
        if mp3_link == -1:
            await message.answer("404..")
        else:
            await message.answer_audio(audio=mp3_link,  reply_markup=user_keyboards.get_showcase_kb(), caption = 'Text')
    # if start_photo =="":
    #     await message.answer(text = text, parse_mode="HTML")
    # else:
    #     await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )

@router.message(F.audio)
#proverka etogo bita v magaze
@new_user_handler
@new_seller_handler
async def new_product(msg: Message, is_clb=False, **kwargs):
    user_id = msg.from_user.id
    performer = msg.audio.performer
    title = msg.audio.title
    name = msg.audio.file_name
    file_id = msg.audio.file_id

    await msg.answer(text = 'Poehali', parse_mode="HTML")
    #proverka etogo bita v magaze
    await ProductsDatabase.create_table()
    await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=file_id)
    
    logger.success(f"New product {name} by {user_id}")




@router.message(Command("homepage"))
@new_user_handler
async def homepage_handler(message: Message, is_clb=False, **kwargs):
    if is_clb:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
    user_id = message.from_user.id
    cart = CartsDatabase.get_value(user_id)
    await message.answer(text = f'Лучший маркетплейс музыки.\n Подписывайтесь на наш канал (линк).',reply_markup = user_keyboards.get_homepage_kb(user_id))

@router.message(Command("settings"))
@new_user_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    if is_clb:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
    user_id = message.from_user.id

    await message.answer(text = f'Settings',reply_markup = user_keyboards.get_settings_kb())