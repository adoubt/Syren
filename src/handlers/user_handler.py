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
async def start_handler(message: Message, is_clb=False, product_id:int| None=None,**kwargs):
    
    if is_clb:
        user_id = message.chat.id
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        user_id = message.from_user.id
        await message.delete()
        data = message.text.split(" ",1)[-1]
        product_id = int(data)
    if message.text != "/start":
        
        product = await ProductsDatabase.get_product(product_id)
        # license_type=5
        # stems_link = product[7]
        # wav_link = product[6]
        mp3_link = product[5]
        # if stems_link =='':
        #     license_type=2
        # if wav_link !='':
        #     license_type=1
        # if mp3_link !='':
        #     license_type=0
        
        
        image_link = product[8]
        is_sold = product[9]
        collab = product[11]
        tags = product[12]
        seller = product[1]
        featured_price = await LicensesDatabase.get_feature_by_user(seller)
        channel = await UsersDatabase.get_value(seller,"channel")
        if mp3_link == -1:
            await message.answer("404..")
        else:
            already_in_cart = 0
            if await CartsDatabase.get_value('product_id',user_id) == product_id:
                already_in_cart = 1
            await message.answer_audio(audio=mp3_link,  reply_markup=user_keyboards.get_showcase_kb(product_id=product_id, price=featured_price,is_sold=is_sold,channel=channel,already_in_cart=already_in_cart), caption = '')
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
    await CartsDatabase.create_table()
    cart_count = await CartsDatabase.get_cart_count(user_id)
    await message.answer(text = f'Лучший маркетплейс музыки.\n Подписывайтесь на наш канал (линк).',reply_markup = user_keyboards.get_homepage_kb(user_id,cart_count))

@router.message(Command("settings"))
@new_user_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    if is_clb:
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
    user_id = message.from_user.id

    await message.answer(text = f'Settings',reply_markup = user_keyboards.get_settings_kb())

@router.callback_query(lambda clb: clb.data == 'start')
@new_user_handler
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await start_handler(clb.message, is_clb=True)

@router.callback_query(lambda clb: clb.data == 'homepage')
@new_user_handler
async def homepage_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await homepage_handler(clb.message, is_clb=True)


@router.callback_query(lambda clb: clb.data == 'settings')
@new_user_handler
async def settings_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await settings_handler(clb.message, is_clb=True)

    


@router.callback_query(lambda clb: clb.data.startswith("showcase"))
@new_user_handler
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = data[1]
    await start_handler(clb.message, is_clb=True,product_id = product_id)

@router.callback_query(lambda clb: clb.data.startswith("choose_license_"))
async def choose_license_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):

    data = clb.data.split('_',2)
    user_id = clb.from_user.id
    product_id = data[2]
    product = await ProductsDatabase.get_product(product_id)
    license_type=5
    seller = product[1]
    stems_link = product[7]
    wav_link = product[6]
    mp3_link = product[5]
    if stems_link =='':
        license_type=2
    if wav_link =='':
        license_type=1
    if mp3_link =='':
        license_type=0
    licenses = await LicensesDatabase.get_licenses_by_user(seller, license_type)
    
    await clb.message.edit_caption(caption = 'Choose license', reply_markup = user_keyboards.get_choose_licenses_kb(user_id,product_id,licenses))


@router.callback_query(lambda clb: clb.data.startswith("addToCart"))
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',3)
    product_id,user_id,license_id = data[1],data[3],data[2]
    product = await ProductsDatabase.get_product(product_id)
    await CartsDatabase.create_table()
    await CartsDatabase.add_to_cart(user_id,product_id,license_id)
    
    seller, is_sold= product[1],product[9]
    channel = await UsersDatabase.get_value(seller,'channel')
    await clb.message.edit_caption(caption = 'Added To Cart ✔', reply_markup = user_keyboards.get_showcase_kb(product_id=product_id,is_sold=is_sold,channel=channel,already_in_cart=1))

@router.message(Command("Cart"))
@new_user_handler
async def cart_handler(message: Message, is_clb=False, **kwargs):
    if is_clb:
        user_id = message.chat.id
        await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        await message.delete()
        user_id = message.from_user.id
    
    if await CartsDatabase.get_cart_count(user_id)==0:
        await CartsDatabase.create_table()
        await message.answer(text = "Your Cart is Empty", reply_markup= user_keyboards.get_homepage_kb(user_id,0))
        return

    cart = await CartsDatabase.get_cart_by_user(user_id)

    for item in cart:
        license_id = item[2]
        license = await LicensesDatabase.get_license(license_id)
        license_name,price,description, license_file = license[2],license[4],license[3],license[7]
        product_id = item[1]
        product = await ProductsDatabase.get_product(product_id)
        mp3_link = product
        mp3_link = product[5]
        seller = product[1]
        await message.answer_audio(audio=mp3_link, reply_markup=user_keyboards.get_item_in_cart_kb(user_id,product_id,license_name,price,description, license_file), caption = f'{license_name}\nYou Will Get {description}\nTotal: {price} USD')



@router.callback_query(lambda clb: clb.data == 'cart')
@new_user_handler
async def cart_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await cart_handler(clb.message, is_clb=True)


@router.callback_query(lambda clb: clb.data.startswith("delItemFromCart"))
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[2]
    await CartsDatabase.del_from_cart(user_id,product_id)
    if await CartsDatabase.get_cart_count(user_id)==0:
        await CartsDatabase.create_table()
        await clb.message.edit_caption(text = "Your Cart is Empty", reply_markup= user_keyboards.get_homepage_kb(user_id,0))
