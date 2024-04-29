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
# from src.methods.payment import aaio_manager
# from src.methods.payment.payment_processing import ProcessOrder

router =  Router()
from src.misc import bot,bot_id, super_admin,password



def new_user_handler(function):
    async def _new_user_handler(*args, **kwargs):
        message: Message = args[0]
        user_id = message.from_user.id
        await UsersDatabase.create_table()
        if (await UsersDatabase.get_user(user_id)) == -1:
            await UsersDatabase.create_user(user_id)
            
            logger.success(f"Новый пользователь (ID: {user_id})")
            if user_id == int(bot_id):

                await UsersDatabase.set_value(user_id,'status',1)
                #назначение бота админом для кнопок в админке(костыль, вроде пофикшен)
                logger.info(f'[Admin] {user_id} получил права админа')
            # else:
                # await message.answer(
                # "👋 Привет, вижу ты новенький. Будем знакомы, чтобы получить список моих команд напиши <code>/help</code>",
                # parse_mode="HTML")


        return await function(*args, **kwargs)

    return _new_user_handler



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
        beat_id = int(data)
        mp3_link = await ProductsDatabase.get_value("mp3_link", beat_id) 
        if mp3_link == -1:
            await message.answer("404..")
        else:
            await message.answer_audio(audio= mp3_link,  reply_markup=user_keyboards.get_licenses_kb(), caption = 'Jopa')
    # if start_photo =="":
    #     await message.answer(text = text, parse_mode="HTML")
    # else:
    #     await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )


@router.callback_query(lambda clb: clb.data == 'start')
@new_user_handler
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await start_handler(clb.message, is_clb=True)
    



@router.message(F.audio)
#proverka etogo bita v magaze
@new_user_handler
async def new_product(msg: Message, is_clb=False, **kwargs):
    user_id = msg.from_user.id
    performer = msg.audio.performer
    title = msg.audio.title
    name = msg.audio.file_name
    file_id = msg.audio.file_id

    await msg.answer(text = 'Poehali', parse_mode="HTML")
    #proverka etogo bita v magaze
    # await ProductsDatabase.create_table()
    await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=file_id)
    
    logger.success(f"New product {name} by {user_id}")