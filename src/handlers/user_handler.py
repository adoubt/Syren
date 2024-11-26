import asyncio
from aiogram import types
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery, InputMediaDocument, InputMediaAudio
from aiogram.fsm.context import FSMContext

from loguru import logger

from src.keyboards import user_keyboards

from src.methods.database.users_manager import UsersDatabase
from src.methods.database.orders_manager import OrdersService
from src.methods.database.carts_manager import ShoppingCartService
from src.methods.database.products_manager import ProductsDatabase
from src.methods.database.licenses_manager import LicensesDatabase
from src.methods.database.licenses_products_manager import LicensesProductsDatabase
from src.methods.database.wishlists_manager import WishlistsDatabase
# from src.methods.database.sales_manager import SalesDatabase
# from src.methods.payment import aaio_manager
# from src.methods.payment.payment_processing import ProcessOrder


router =  Router()

from src.misc import bot,bot_id, SUPER_ADMIN,PASSWORD, SERVICE_FEE
from src.handlers.decorators import new_seller_handler, new_user_handler

import pytonconnect.exceptions
from pytoniq_core import Address
from pytonconnect import TonConnect


from src.methods.payment.TON.messages import get_comment_message
from src.methods.payment.TON.connector import get_connector

@router.message(Command("start"))
@new_user_handler
async def start_handler(message: Message, is_clb=False, product_id:int| None=None,**kwargs):
    await WishlistsDatabase.create_table()
    

    if is_clb:
        user_id = message.chat.id
        # wishlist_count = await WishlistsDatabase.get_wishlist_count(user_id)
        # await message.answer(text= text,reply_markup = user_keyboards.get_main_buyer_kb(wishlist_count))
    #     # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    if not is_clb:
        text = 'Welcome, here '
        user_id = message.from_user.id
        wishlist_count = await WishlistsDatabase.get_wishlist_count(user_id)
        # await message.delete()
        await message.answer(text=text, reply_markup = user_keyboards.get_main_buyer_kb(wishlist_count))
   
    
    connector = get_connector(user_id)
    connected = await connector.restore_connection()

    if message.text != "/start" and message.text!="🌏 Buy Beats":
        if product_id is None:
            data = message.text.split(" ",1)[-1]
            product_id = int(data)
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
            already_in_wishlist = 0
            if await WishlistsDatabase.get_value('product_id',user_id) == product_id:
                already_in_wishlist = 1
            if is_clb:
                await message.edit_caption( reply_markup=user_keyboards.get_showcase_kb(product_id=product_id, price=featured_price,is_sold=is_sold,channel=channel,already_in_wishlist=already_in_wishlist), caption = '')
            else: 
                await message.answer_audio(audio=mp3_link,  reply_markup=user_keyboards.get_showcase_kb(product_id=product_id, price=featured_price,is_sold=is_sold,channel=channel,already_in_wishlist=already_in_wishlist), caption = '')
    # if start_photo =="":
    #     await message.answer(text = text, parse_mode="HTML")
    # else:
    #     await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )


@router.callback_query(lambda clb: clb.data.startswith("showcase"))
@new_user_handler
async def showcase_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = data[1]
    await start_handler(clb.message, is_clb=True,product_id = product_id)



@router.message(F.text == "🏠 Home")
@new_user_handler
async def homepage_handler(message: Message, is_clb=False, **kwargs):
  
    user_id = message.from_user.id
    await WishlistsDatabase.create_table()
    wishlist_count = await WishlistsDatabase.get_wishlist_count(user_id)
    await message.answer(text = f'Лучший маркетплейс музыки.\n Подписывайтесь на наш канал (линк).',reply_markup = user_keyboards.get_homepage_kb(user_id,wishlist_count))

@router.message(F.text == "⚙️ Settings")
@new_user_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    # if is_clb:
    #     await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    # else:
    #     await message.delete()
    user_id = message.from_user.id

    await message.answer(text = f'Settings',reply_markup = user_keyboards.get_settings_kb())

@router.message(F.text == "🌏 Sell Beats")
async def seller_handler(message: Message, is_clb=False, **kwargs):
    await message.answer(text='Seller Welcome MSG', reply_markup=user_keyboards.get_main_seller_kb())

@router.message(F.text == "🌏 Buy Beats")
async def buyer_handler(message: Message, is_clb=False, **kwargs):
    await start_handler(message)

@router.message(F.text == "🤍 Wishlist")
@new_user_handler
async def mybeats_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.from_user.id
    if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        await WishlistsDatabase.create_table()
        await message.answer(text = "Your Wishlist is Empty")
        return

    wishlist = await WishlistsDatabase.get_wishlist_by_user(user_id)

    for item in wishlist:
        product_id = item[1]
        product = await ProductsDatabase.get_product(product_id)
        #Лишний раз лезу в бд
        mp3_link = product[5]
        await message.answer_audio(audio=mp3_link, reply_markup=user_keyboards.get_item_in_wishlist_kb(user_id,product_id))

@router.message(F.text == "🛒 Cart")
@new_user_handler
async def generate_cart_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    user_id = message.from_user.id
    if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        await WishlistsDatabase.create_table()
        await message.answer(text = "Your Cart is Empty")
        return

    wishlist = await WishlistsDatabase.get_wishlist_by_user(user_id)

    for item in wishlist:
        product_id = item[1]
        product = await ProductsDatabase.get_product(product_id)
        #Лишний раз лезу в бд
        mp3_link = product[5]
        await message.answer_audio(audio=mp3_link, reply_markup=user_keyboards.get_item_in_wishlist_kb(user_id,product_id))

        
@router.message(F.text == "📼 My Beats")
@new_user_handler
async def mybeats_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
    if is_clb:
        user_id = message.chat.id
        # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        # await message.delete()
        user_id = message.from_user.id
    total_beats = await ProductsDatabase.get_count_by_user(user_id)
    if total_beats == 0:
        await message.answer('Nothing uploaded yet, go to ➕ New Beat')
        return
    total_pages = (total_beats //10) + 1
    if current_page >= total_pages:
        current_page = total_pages
    if current_page < 0:
        current_page = 0
    
    beats = await ProductsDatabase.get_all_by_user(user_id, current_page*10)
    if is_clb:
        await message.edit_text(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))
    else:
        await message.answer(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))

@router.message(F.text == "📂 My Licenses")
@new_user_handler
async def mylicenses_handler(message: Message, is_clb=False, **kwargs):
    user_id = message.chat.id if is_clb else message.from_user.id
    licenses = await LicensesDatabase.get_licenses_by_user(user_id=user_id, active_only=0)

    text = "Licenses:"
    keyboard = user_keyboards.get_licenses_kb(licenses)

    if is_clb:
        await message.edit_text(text=text, reply_markup=keyboard)
    else:
        await message.answer(text=text, reply_markup=keyboard)


@router.callback_query(lambda clb: clb.data == 'mylicenses')
@new_user_handler
async def mylicenses_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await mylicenses_handler(clb.message, is_clb=True)
# @router.message(F.text == "📼 My Beats")
# @new_user_handler
# async def mybeats_handler(message: Message, is_clb=False,current_page:int|None = 0,**kwargs):
#     if is_clb:
#         user_id = message.chat.id
#         # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
#     else:
#         # await message.delete()
#         user_id = message.from_user.id
#     total_beats = await ProductsDatabase.get_count_by_user(user_id)
#     if total_beats == 0:
#         await message.answer('Nothing uploaded yet, go to ➕ New Beat')
#         return
#     total_pages = (total_beats //10) + 1
#     if current_page >= total_pages:
#         current_page = total_pages
#     if current_page < 0:
#         current_page = 0
    
#     beats = await ProductsDatabase.get_all_by_user(user_id, current_page*10)
#     if is_clb:
#         await message.edit_text(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))
#     else:
#         await message.answer(text=f'My Beats ({total_beats}):', reply_markup=user_keyboards.get_my_beats_kb(beats, current_page,total_pages))


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
    await clb.answer()

@router.callback_query(lambda clb: clb.data.startswith("choose_license_"))
async def choose_license_clb_handler(clb: CallbackQuery, is_clb=True, data:str|None = None, **kwargs):
    if is_clb:
        data = clb.data.split('_',2)
        in_cart = None 
    else:
        data = clb.data.split('_',3)
        in_cart = int(data[3])#тут лежит лицуха из корзины логика такая если id совпадет то будет другая кнопка
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
    await LicensesProductsDatabase.create_table()
    disabled = await LicensesProductsDatabase.get_disabled(product_id)
    await clb.message.edit_caption(caption = 'Choose license', reply_markup = user_keyboards.get_choose_licenses_kb(user_id,product_id,licenses,disabled,in_cart))


@router.callback_query(lambda clb: clb.data.startswith("addTowishlist"))
async def addTowishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',3)
    user_id,product_id, = data[1],data[1]
    product = await ProductsDatabase.get_product(product_id)
    await WishlistsDatabase.create_table()
    await WishlistsDatabase.add_to_wishlist(user_id,product_id)
    
    seller, is_sold= product[1],product[9]
    channel = await UsersDatabase.get_value(seller,'channel')
    await clb.message.edit_caption(caption = 'Added To wishlist ✔', reply_markup = user_keyboards.get_showcase_kb(product_id=product_id,is_sold=is_sold,channel=channel,already_in_wishlist=1))


# @router.callback_query(lambda clb: clb.data.startswith("addTowishlist"))
# async def addTowishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
#     data = clb.data.split('_',3)
#     product_id,user_id, = data[1],data[3],data[1]
#     product = await ProductsDatabase.get_product(product_id)
#     await WishlistsDatabase.create_table()
#     await WishlistsDatabase.add_to_wishlist(user_id,product_id,license_id)
    
#     seller, is_sold= product[1],product[9]
#     channel = await UsersDatabase.get_value(seller,'channel')
#     await clb.message.edit_caption(caption = 'Added To wishlist ✔', reply_markup = user_keyboards.get_showcase_kb(product_id=product_id,is_sold=is_sold,channel=channel,already_in_wishlist=1))

# @router.message(F.text.startswith("🛒 wishlist"))
# @new_user_handler
# async def wishlist_handler(message: Message, is_clb=False, **kwargs):
#     if is_clb:
#         user_id = message.chat.id
#         # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
#     else:
#         # await message.delete()
#         user_id = message.from_user.id
    
#     if await WishlistsDatabase.get_wishlist_count(user_id)==0:
#         await WishlistsDatabase.create_table()
#         await message.edit_text(text = "Your wishlist is Empty", reply_markup= user_keyboards.get_homepage_kb(user_id,0))
#         return

#     wishlist = await WishlistsDatabase.get_wishlist_by_user(user_id)

#     for item in wishlist:
#         license_id = item[2]
#         license = await LicensesDatabase.get_license(license_id)
#         license_name,price,description, license_file = license[2],license[4],license[3],license[7]
#         product_id = item[1]
#         product = await ProductsDatabase.get_product(product_id)
#         mp3_link = product
#         mp3_link = product[5]
#         seller = product[1]
#         await message.answer_audio(audio=mp3_link, reply_markup=user_keyboards.get_item_in_wishlist_kb(user_id,product_id,license_name,price,description, license_file), caption = f'{license_name}\nYou Will Get {description}\nTotal: {price} USD')



# @router.callback_query(lambda clb: clb.data == 'wishlist')
# @new_user_handler
# async def wishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
#     await wishlist_handler(clb.message, is_clb=True)


@router.callback_query(lambda clb: clb.data.startswith("delItemFromwishlist"))
async def delItemFromwishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[1]
    await WishlistsDatabase.del_from_wishlist(user_id,product_id)
    if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        await WishlistsDatabase.create_table()
        await clb.message.edit_caption(text = "Your wishlist is Empty")

@router.callback_query(lambda clb: clb.data.startswith("delItemFromwishlist"))
async def delItemFromwishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[1]
    await WishlistsDatabase.del_from_wishlist(user_id,product_id)
    if await WishlistsDatabase.get_wishlist_count(user_id)==0:
        await WishlistsDatabase.create_table()
        await clb.message.edit_caption(text = "Your wishlist is Empty")



@router.callback_query(lambda clb: clb.data.startswith('mybeats'))
@new_user_handler
async def mybeats_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    current_page = int(data[1])
    await mybeats_handler(clb.message, is_clb=True,current_page = current_page)

@router.callback_query(lambda clb: clb.data.startswith('licenses'))
@new_user_handler
async def licenses_clb_handler(clb: CallbackQuery, product_id:int|None = None, is_clb=False, **kwargs):
    if product_id == None:
        data = clb.data.split('_',1)
        product_id = int(data[1])
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
    await LicensesProductsDatabase.create_table()
    disabled = await LicensesProductsDatabase.get_disabled(product_id)
    if is_clb:
        await bot.edit_message_reply_markup(chat_id=clb.message.chat.id, message_id=clb.message.message_id,reply_markup = user_keyboards.get_product_licenses_kb(product_id, licenses,disabled))
    else:
        await clb.message.edit_text(text=f'Licenses:',reply_markup = user_keyboards.get_product_licenses_kb(product_id, licenses,disabled))   
@router.callback_query(lambda clb: clb.data.startswith('files'))
@new_user_handler
async def files_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = int(data[1])
    await clb.message.edit_text(text='Files:\n(tap to show)',reply_markup = user_keyboards.get_files_kb(product_id))   

@router.callback_query(lambda clb: clb.data.startswith('showfile_'))
@new_user_handler
async def showfile_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    if data[1] == 'mp3':
        await clb.message.answer_audio(audio = mp3_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'wav': 
        await clb.message.answer_document(document = wav_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'stems':
        await clb.message.answer_document(document = stems_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'preview':
        await clb.message.answer_audio(audio = preview_link,reply_markup =user_keyboards.get_hide_file_kb())  

class EditFile(StatesGroup):
    file_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('editfile_'))
@new_user_handler
async def showfile_clb_handler(clb: CallbackQuery, state = FSMContext, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[1])
    await state.set_data([product_id,data[1]])
    if data[1] == 'mp3':
        text = 'Upload or forward .MP3'
    elif data[1] == 'wav':
        text = 'Upload or forward .WAV'
    elif data[1] == 'stems':
        text = 'Upload or forward .ZIP (or other archive)'
    elif data[1] == 'preview':
        text = 'Upload or forward .MP3'
    await state.set_state(EditFile.file_ask)
    await clb.message.edit_text(text=text,reply_markup =user_keyboards.get_edit_file_back_kb(product_id))

@router.message(EditFile.file_ask)
async def file_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    data = await state.get_data() 
    product_id= data[0]
    if message.audio is None or message.document is None:
        await state.clear()
        return
    if data[1] == 'mp3':
        link = message.audio.file_id
    elif data[1] == 'wav':
        link = message.document.file_id
    elif data[1] == 'stems':
        link = message.document.file_id
    elif data[1] == 'preview':
        link = message.audio.file_id
    await state.clear()
    await ProductsDatabase.set_value(product_id,f'{data[1]}_link',link )
    await message.answer(text=f'Updated!\nFiles:',reply_markup = user_keyboards.get_files_kb(product_id))


@router.callback_query(lambda clb: clb.data == 'hide_file')
async def hide_file_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.message.delete()

@router.callback_query(lambda clb: clb.data.startswith('enable'))
async def enable_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[1]
    license_id = clb.data.split('_',2)[2]
    await LicensesProductsDatabase.del_row(license_id,product_id)
    await licenses_clb_handler(clb, product_id,is_clb=True)

@router.callback_query(lambda clb: clb.data.startswith('disable'))
async def disable_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[1]
    license_id = clb.data.split('_',2)[2]
    await LicensesProductsDatabase.create(product_id,license_id,1)
    await licenses_clb_handler(clb, product_id,is_clb=True)

@router.callback_query(lambda clb: clb.data.startswith('delproduct'))
async def delproduct_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',2)[2]
    is_sure = clb.data.split('_',2)[1]
    if is_sure =='0':
        await clb.message.edit_text(text = 'Are You Sure?', reply_markup=user_keyboards.get_delbeat_kb(product_id))
        return
    await ProductsDatabase.del_product(product_id)
    await clb.message.edit_text(text='Deleted')

@router.callback_query(lambda clb: clb.data.startswith('delproduct_sure_'))
async def del_sure_product_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    product_id = clb.data.split('_',1)[1]
    await clb.message.edit_text(text = 'Are You Sure?', reply_markup=user_keyboards.get_delbeat_kb(product_id))

class EditProductNameState(StatesGroup):
    name_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('editproductname'))
async def editproductname_handler(clb: CallbackQuery, state: FSMContext, is_clb=False, **kwargs):
    product_id = int(clb.data.split('_',2)[1])
    await state.set_state(EditProductNameState.name_ask)
    await state.set_data([product_id,clb])
    await clb.message.edit_text(text='Type New Name...', reply_markup=user_keyboards.get_editbeatname_kb(product_id))

@router.message(EditProductNameState.name_ask)
async def name_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    name = message.text
    data = await state.get_data() 
    product_id= data[0]
    clb = data[1]
    await ProductsDatabase.set_value(product_id,'name', name) 
    await state.clear()
    await message.delete()
    await beat_clb_handler(clb,product_id)
    # await beat_handler(product_id)

@router.callback_query(lambda clb: clb.data.startswith("delItemFromwishlist"))
async def delItemFromwishlist_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[1]

class NewBeatState(StatesGroup):
    mp3_ask = State()
    wav_ask = State()
    stems_ask = State()
    preview_ask = State()

@router.message(F.text =="➕ New Beat")
@new_user_handler
async def newbeat_handler(message: Message,state: FSMContext, is_clb=False,**kwargs):
    await state.set_state(NewBeatState.mp3_ask)
    await message.answer(text= f'Upload or forward .MP3', reply_markup = user_keyboards.get_cancel_kb())

@router.callback_query(lambda clb: clb.data == 'cancel')
async def cancel_handler(clb: CallbackQuery,state = FSMContext, is_clb=False, **kwargs) -> None:
    
    await clb.message.delete()
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()



@router.message(NewBeatState.mp3_ask)
async def mp3_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    user_id = message.from_user.id
    if message.audio is None or message.document is None:
        
        await state.clear()
    performer = message.audio.performer
    title = message.audio.title
    name = message.audio.file_name
    mp3_link = message.audio.file_id

    #proverka etogo bita v magaze
    

    await state.set_state(NewBeatState.wav_ask)
    await state.set_data([user_id,performer,title,name,mp3_link])
    await message.answer(text= f'Upload or forward .WAV', reply_markup = user_keyboards.get_cancel_kb())

@router.message(NewBeatState.wav_ask)
async def wav_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    data = await state.get_data() 
    user_id = data[0]
    performer = data[1]
    title = data[1]
    name = data[3]
    mp3_link = data[4]
    wav_link = message.document.file_id
    
    await state.set_state(NewBeatState.stems_ask)
    await state.set_data([user_id,performer,title,name,mp3_link,wav_link])
    await message.answer(text= f'Upload or forward .ZIP',reply_markup = user_keyboards.get_newbeat_kb())

@router.callback_query(lambda clb: clb.data == 'skip_stems')
async def skip_stems_handler(clb: CallbackQuery, state : FSMContext, is_clb=False, **kwargs):
    await state.set_state(NewBeatState.stems_ask)
    await stems_ask_callback_handler(message = clb.message,state= state, is_skip=True,is_clb=True)
    await clb.answer()
@router.message(NewBeatState.stems_ask)
async def stems_ask_callback_handler(message: types.Message, state: FSMContext,is_clb=False, is_skip= False,**kwargs):
    
    data = await state.get_data() 
    user_id = data[0]
    performer = data[1]
    title = data[1]
    name = data[3]
    mp3_link = data[4]
    wav_link = data[5]
    await state.clear()
    await ProductsDatabase.create_table()
    if is_skip:
        await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=mp3_link,wav_link=wav_link, preview_link=mp3_link)
    
    else:
        stems_link = message.document.file_id
        await ProductsDatabase.create_product(user_id = user_id,name = name,mp3_link=mp3_link,wav_link=wav_link,stems_link=stems_link, preview_link=mp3_link)
    
    
    logger.success(f"New product {name} by {user_id}")
    await message.answer(text= f'Created, go to 📼 My Beats')

@router.callback_query(lambda clb: clb.data.startswith('beat'))
async def beat_clb_handler(clb: CallbackQuery, product_id:int|None=None,is_clb=False, **kwargs):
    
    if product_id is None:
        data = clb.data.split('_',1)
        product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id) 
    link = f't.me/OctarynBot?start={product_id}'
    name = product[2]
    await clb.message.edit_text(text=f'<b>{name}</b>\n\n(tap to copy link):\n<code>{link}</code>',parse_mode="HTML",reply_markup=user_keyboards.get_beat_kb(product_id))


@router.callback_query(lambda clb: clb.data == 'setdefaultlicenses')
async def setdefaultlicenses_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    user_id = clb.message.chat.id
    await LicensesDatabase.set_default(user_id)
    await mylicenses_handler(clb.message, is_clb=True)
    await clb.answer()

class NewLicense(StatesGroup):
    file_ask = State()

@router.callback_query(lambda clb: clb.data == 'newlicense')
async def newlicense_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    user_id = clb.message.chat.id

    await LicensesDatabase.create_license(user_id)
    await mylicenses_handler(clb.message, is_clb=True)    

@router.callback_query(lambda clb: clb.data.startswith('mylicense_'))
async def mylicense_clb_handler(clb: CallbackQuery, license_id:int|None=None,is_clb=False, **kwargs):
    if license_id is None:
        data = clb.data.split('_',1)
        license_id = int(data[1])
    license = await LicensesDatabase.get_license(license_id) 
    is_archived,feature, is_active = license[9], license[5], license[11]
    meta_preview = ''
    if is_archived == 1:
        meta_preview += '🗃'
    if feature ==1:
        meta_preview += '⭐️'
    if is_active !=1:
        meta_preview +='💤'
    await clb.message.edit_text(text=f'{meta_preview}<b>{license[2]}</b>',parse_mode="HTML",reply_markup=user_keyboards.get_mylicense_kb(license))

class LicenseEdit(StatesGroup):
    name_ask = State()
    desc_ask = State()
    price_ask = State()
    upload_ask = State()

@router.callback_query(lambda clb: clb.data.startswith('licenseedit'))
async def licenseedit_clb_handler(clb: CallbackQuery,is_clb=False, state = FSMContext, **kwargs):
    
    user_id = clb.message.chat.id
    data = clb.data.split('_',3)
    license_id = data[2]
    if data[1] == 'name':
        await state.set_state(LicenseEdit.name_ask)
        await clb.message.edit_text(text = 'Imput new name',reply_markup=user_keyboards.get_cancel_kb())
    elif data[1] == 'decs':
        await state.set_state(LicenseEdit.desc_ask)
        await clb.message.edit_text(text = 'Imput new description',reply_markup=user_keyboards.get_cancel_kb())
    elif data[1] == 'type': 
        pass
    
    elif data[1] == 'active':
        r = await LicensesDatabase.toggle_license_active(license_id)
        if r ==-1:
            await clb.message.edit_text(text = 'Error: Some fields are empty')
        else:
            await mylicense_clb_handler(clb,license_id)
    elif data[1] == 'price':
        await state.set_state(LicenseEdit.price_ask)
        await clb.message.edit_text(text = 'Imput new price',reply_markup=user_keyboards.get_cancel_kb())
        
    elif data[1] == 'feature':
        if data[3] == '1':
            await LicensesDatabase.set_featured_license(user_id, license_id)
        else:
            await LicensesDatabase.set_value(license_id,"feature",0)
        await mylicense_clb_handler(clb,license_id)

    elif data[1] == 'showfile':
        license= await LicensesDatabase.get_license(license_id)
        license_file = license[8]
        await clb.message.answer_document(document = license_file,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'uploadfile':
        await state.set_state(LicenseEdit.upload_ask)
        await state.set_data([license_id])
        await clb.message.edit_text(text = 'Upload or forward yor contract file',reply_markup=user_keyboards.get_cancel_kb())
    elif data[1] == 'delete': pass   

@router.message(LicenseEdit.upload_ask)
async def upload_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    data = await state.get_data() 
    license_id= data[0]
    if message.document is None:
        await state.clear()
        return
    license_file = message.document.file_id
    
    await state.clear()
    await LicensesDatabase.set_value(license_id,"license_file",license_file)
    await message.answer(text=f'Updated!',reply_markup =user_keyboards.get_hide_file_kb())


#Cart
@router.callback_query(lambda clb: clb.data.startswith('addToCart'))
async def addToCart_clb_handler(clb: CallbackQuery,is_clb=True, **kwargs):
    user_id = clb.message.chat.id
    data = clb.data.split('_',3)
    product_id = int(data[1])
    license_id = int(data[2])
    added_at = clb.message.date
    await ShoppingCartService.add_item(user_id,product_id,license_id,added_at)
    await choose_license_clb_handler(clb,is_clb=False,data = f'choose_license_{product_id}_{license_id}')

@router.callback_query(lambda clb: clb.data.startswith('delFromCart'))
async def delFromCart_clb_handler(clb: CallbackQuery,is_clb=True, **kwargs):
    user_id = clb.message.chat.id
    data = clb.data.split('_',3)
    product_id = int(data[1])
    await ShoppingCartService.remove_item(user_id,product_id)
    await choose_license_clb_handler(clb,is_clb=False,data = f'choose_license_{product_id}_0')


#Stars_payment
   
@router.callback_query(F.data == "paystarscancel")
async def on_paystars_cancel(callback: CallbackQuery, **kwargs):
    # await callback.answer(l10n.format_value("donate-cancel-payment"))

    await callback.message.delete()

@router.callback_query(lambda clb: clb.data.startswith('paystars'))
async def paystars_clb_handler(clb: CallbackQuery,is_clb=False,  **kwargs):
    
    user_id = clb.message.chat.id
    
    data = clb.data.split('_',3)
 
    product_id = int(data[1])
    license_id = int(data[2])

    amount = await LicensesDatabase.get_value('price',license_id)
    prices = [LabeledPrice(label="XTR", amount=amount)]


    await clb.message.answer_invoice(
    title='Invoice Title',
    description=f'You want to pay {amount} XTR(stars)',
    prices=prices,

    # provider_token оставляем пустым
    provider_token="",

    # тут передаем любые данные (пэйлоад)
    # например, идентификатор услуги которую покупает юзер
    # или уровень подписки
    # или еще что-то такое
    # мы же передадим кол-во. задоначенных звёзд (просто так)
    payload=f"paystars_{product_id}_{license_id}_{amount}",

    # XTR - это код валюты Telegram Stars
    currency="XTR",

    # не забываем передать нашу кастомную клавиатуру
    # напоминаю, что это можно не делать
    # ТГ сам добавит кнопку оплаты, если тут ничего не передавать
    reply_markup=user_keyboards.get_paystars_kb(amount)
    )

@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery):
    # смысл on_pre_checkout_query такой же, как и в любых других платежах
    # бот должен ответить в течение 10 секунд
    # ..
    payload = query.invoice_payload
    data = payload.split('_',3)
    product_id = int(data[1])
    license_id = int(data[2])
    amount = int(data[3])
    
    
    # тут можно/нужно проверить доступность товара/услуги, прямо перед оплатой
    product = await ProductsDatabase.get_product(product_id)
    is_sold = product[9]
    
    license = LicensesDatabase.get_license(license_id)
    price = license[4]
    is_active = license[11]
    # добавить проверку наличия файлов
    # дорбавить проверку работы шлюза у битмаря и платформы?
    if is_sold == 1:
        await query.answer(
       ok=False,
       error_message="Unfortunately the beat just has been SOLD"
        )
    elif price != amount:
        await query.answer(
       ok=False,
       error_message="Sorry, the price just was changed"
        )
    elif is_active == 0:
        await query.answer(
       ok=False,
       error_message="Sorry this license was disabled, contact seller for more"
        )
    else :
        await query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message) -> None:
    # await bot.refund_star_payment(
    #     user_id=message.from_user.id,
    #     telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    # )

    customer_id = message.from_user.id
    payload = message.invoice_payload
    data = payload.split('_',3)
    invoice = message.telegram_payment_charge_id
    product_id = int(data[1])
    license_id = int(data[2])
    amount = message.total_amount #int(data[3])

    license = LicensesDatabase.get_license(license_id)
    license_type,license_file = license[6],license[8]

    product = ProductsDatabase.get_product(product_id)
    seller_id, mp3_link,wav_link, stems_link,collab= product[1],product[5],product[6],product[7],product[11]

    promo_code_id = None
    offer_id = None
    payment_method = 'STARS'
    discount = 0.00 # должно быть в payload
    total_amount = (amount * (100-SERVICE_FEE)) - discount
    
    currency = 'XTR'


    logger.success(f"Sale! Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}")
    #Формирую sale
    try:

        await SalesDatabase.create_sale(customer_id,
                                        seller_id,
                                        product_id,
                                        total_amount,
                                        currency,
                                        discount,
                                        SERVICE_FEE,
                                        license_file,
                                        promo_code_id,
                                        invoice,
                                        payment_method,
                                        offer_id)
    except Exception as e:
        await bot.send_message(chat_id =SUPER_ADMIN, text = f'Error while creating Sale after success payment. \nSeller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}\n{e}')
        logger.error(f'Error while creating Sale after success payment. \n Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}')
        await message.answer(text=f'Some problems, I got this msg and will fix ASAP!!!!! you can contact me btw @brokeway')
        await bot.send_message(chat_id = seller_id,text = f'Yo, we\'ve problems with the delivery of your files, fix it or send it manually (buyer contacts in the menu/sales)')
    #Отправляю товары
    try:
        # Базовый массив media с первым элементом, который будет всегда
        media = [InputMediaAudio(media=mp3_link, caption="Caption_mp3")]

        # Добавляем дополнительные элементы в зависимости от license_type
        if license_type in [2, 5, 4, 3]:
            media.append(InputMediaDocument(media=wav_link, caption="Caption_wav"))
        if license_type in [5, 4, 3]:
            media.append(InputMediaDocument(media=stems_link, caption="Caption_stems"))
        media.append(InputMediaDocument(media=license_file, caption="License_file"))
        # Отправляем медиа-группу
        await bot.send_media_group(chat_id=message.chat.id, media=media)
    except Exception as e:
        await bot.send_message(chat_id =SUPER_ADMIN, text = f'Files after success payment wasn\'t delivered. \nSeller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}\n{e}')
        logger.error(f'Files after success payment wasn\'t delivered. \n Seller: {seller_id} Customer: {customer_id} product_id= {product_id} XTR: {amount}')
    #Ставлю SOLD после продажи
    if license_type == 5:
        await ProductsDatabase.set_value(product_id,'is_sold',1)
    
    
    #Уведомляю продавца
    await bot.send_message(chat_id = seller_id, text =f'Congratulations! You’ve made a sale!')# тут будет клава к продаже поближе
    #приват канал для регистрации всех транзакций тут же