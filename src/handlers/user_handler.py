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
    await CartsDatabase.create_table()
    if is_clb:
        user_id = message.chat.id
        cart_count = await CartsDatabase.get_cart_count(user_id)
        await message.edit_text(text='Welcome ', reply_markup = user_keyboards.get_main_buyer_kb(cart_count))
        # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        user_id = message.from_user.id
        cart_count = await CartsDatabase.get_cart_count(user_id)
        # await message.delete()
        await message.answer(text='Welcome', reply_markup = user_keyboards.get_main_buyer_kb(cart_count))
   
    
   

    if message.text != "/start":
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
            already_in_cart = 0
            if await CartsDatabase.get_value('product_id',user_id) == product_id:
                already_in_cart = 1
            await message.answer_audio(audio=mp3_link,  reply_markup=user_keyboards.get_showcase_kb(product_id=product_id, price=featured_price,is_sold=is_sold,channel=channel,already_in_cart=already_in_cart), caption = '')
    # if start_photo =="":
    #     await message.answer(text = text, parse_mode="HTML")
    # else:
    #     await message.answer_photo(photo =start_photo,caption=text,parse_mode="HTML" )






@router.message(F.text == "🏠 Home")
@new_user_handler
async def homepage_handler(message: Message, is_clb=False, **kwargs):
  
    user_id = message.from_user.id
    await CartsDatabase.create_table()
    cart_count = await CartsDatabase.get_cart_count(user_id)
    await message.answer(text = f'Лучший маркетплейс музыки.\n Подписывайтесь на наш канал (линк).',reply_markup = user_keyboards.get_homepage_kb(user_id,cart_count))

@router.message(F.text == "⚙️ Settings")
@new_user_handler
async def settings_handler(message: Message, is_clb=False, **kwargs):
    # if is_clb:
    #     await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    # else:
    #     await message.delete()
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
async def addToCart_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',3)
    product_id,user_id,license_id = data[1],data[3],data[2]
    product = await ProductsDatabase.get_product(product_id)
    await CartsDatabase.create_table()
    await CartsDatabase.add_to_cart(user_id,product_id,license_id)
    
    seller, is_sold= product[1],product[9]
    channel = await UsersDatabase.get_value(seller,'channel')
    await clb.message.edit_caption(caption = 'Added To Cart ✔', reply_markup = user_keyboards.get_showcase_kb(product_id=product_id,is_sold=is_sold,channel=channel,already_in_cart=1))

@router.message(F.text.startswith("🛒 Cart"))
@new_user_handler
async def cart_handler(message: Message, is_clb=False, **kwargs):
    if is_clb:
        user_id = message.chat.id
        # await bot.delete_message(chat_id=message.chat.id,message_id=message.message_id)
    else:
        # await message.delete()
        user_id = message.from_user.id
    
    if await CartsDatabase.get_cart_count(user_id)==0:
        await CartsDatabase.create_table()
        await message.edit_text(text = "Your Cart is Empty", reply_markup= user_keyboards.get_homepage_kb(user_id,0))
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
async def delItemFromCart_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[2]
    await CartsDatabase.del_from_cart(user_id,product_id)
    if await CartsDatabase.get_cart_count(user_id)==0:
        await CartsDatabase.create_table()
        await clb.message.edit_caption(text = "Your Cart is Empty", reply_markup= user_keyboards.get_homepage_kb(user_id,0))


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

@router.callback_query(lambda clb: clb.data.startswith('mybeats'))
@new_user_handler
async def mybeats_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    current_page = int(data[1])
    await mybeats_handler(clb.message, is_clb=True,current_page = current_page)

@router.callback_query(lambda clb: clb.data.startswith('files'))
@new_user_handler
async def files_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = int(data[1])
    await clb.message.edit_text(text='Files:',reply_markup = user_keyboards.get_files_kb(product_id))   

@router.callback_query(lambda clb: clb.data.startswith('showfile_'))
@new_user_handler
async def files_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',2)
    product_id = int(data[2])
    product = await ProductsDatabase.get_product(product_id)
    preview_link,mp3_link,wav_link,stems_link = product[4],product[5],product[6],product[7]
    if data[1] == 'mp3':
        await bot.send_audio(chat_id = clb.message.chat.id, audio = mp3_link,reply_markup =user_keyboards.get_hide_file_kb())
    elif data[1] == 'wav': 
        await bot.send_document(chat_id = clb.message.chat.id, document = wav_link)
    elif data[1] == 'stems':
        await bot.send_document(chat_id = clb.message.chat.id, document = stems_link)
    elif data[1] == 'preview':
        await bot.send_audio(chat_id = clb.message.chat.id, audio = preview_link)


    await clb.message.edit_text(text='Files:',reply_markup = user_keyboards.get_files_kb(product_id))  

@router.callback_query(lambda clb: clb.data == 'hide_file')
async def hide_file_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await clb.message.delete()

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
    await state.set_data([product_id])
    await clb.message.edit_text(text='Type New Name...', reply_markup=user_keyboards.get_editbeatname_kb(product_id))
@router.message(EditProductNameState.name_ask)
async def name_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    name = message.text
    data = await state.get_data() 
    product_id= data[0]
    await ProductsDatabase.set_value(product_id,'name', name) 
    await state.clear()
    await beat_handler(product_id)
@router.callback_query(lambda clb: clb.data.startswith("delItemFromCart"))
async def delItemFromCart_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    
    data = clb.data.split('_',2)
    user_id,product_id = data[1],data[2]

class NewBeatState(StatesGroup):
    mp3_ask = State()
    wav_ask = State()
    stems_ask = State()
    preview_ask = State()

@router.message(F.text =="➕ New Beat")
@new_user_handler
async def newbeat_handler(message: Message,state: FSMContext, is_clb=False,**kwargs):
    await state.set_state(NewBeatState.mp3_ask)
    await message.answer(text= f'MP3 File\nUpload or forward .MP3')

@router.message(NewBeatState.mp3_ask)
async def mp3_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    user_id = message.from_user.id
    performer = message.audio.performer
    title = message.audio.title
    name = message.audio.file_name
    mp3_link = message.audio.file_id

    #proverka etogo bita v magaze
    

    await state.set_state(NewBeatState.wav_ask)
    await state.set_data([user_id,performer,title,name,mp3_link])
    await message.answer(text= f'WAV File\nUpload or forward .WAV')

@router.message(NewBeatState.wav_ask)
async def wav_ask_callback_handler(message: types.Message, state: FSMContext, **kwargs):
    
    data = await state.get_data() 
    user_id = data[0]
    performer = data[1]
    title = data[2]
    name = data[3]
    mp3_link = data[4]
    wav_link = message.document.file_id
    
    await state.set_state(NewBeatState.stems_ask)
    await state.set_data([user_id,performer,title,name,mp3_link,wav_link])
    await message.answer(text= f'Stems Archive\nUpload or forward .ZIP',reply_markup = user_keyboards.get_newbeat_kb())

@router.callback_query(lambda clb: clb.data == 'skip_stems')
async def current_page_handler(clb: CallbackQuery, state : FSMContext, is_clb=False, **kwargs):
    await state.set_state(NewBeatState.stems_ask)
    await stems_ask_callback_handler(message = clb.message,state= state, is_skip=True,is_clb=True)
    await clb.answer()
@router.message(NewBeatState.stems_ask)
async def stems_ask_callback_handler(message: types.Message, state: FSMContext,is_clb=False, is_skip= False,**kwargs):
    
    data = await state.get_data() 
    user_id = data[0]
    performer = data[1]
    title = data[2]
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

@router.message(F.text == "41beat")
async def beat_handler(product_id):
    product = await ProductsDatabase.get_product(product_id) 
    link = f't.me/OctarynBot?start={product_id}'
    name = product[2]
    user_id = product[1]
    await bot.send_message(chat_id = user_id,text=f'<b>{name}</b>\n\n<code>{link}</code>\n(tap to copy link)',parse_mode="HTML",reply_markup=user_keyboards.get_beat_kb(product_id))



@router.callback_query(lambda clb: clb.data.startswith('beat'))
async def beat_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    data = clb.data.split('_',1)
    product_id = int(data[1])
    product = await ProductsDatabase.get_product(product_id) 
    link = f't.me/OctarynBot?start={product_id}'
    name = product[2]
    await clb.message.edit_text(text=f'<b>{name}</b>\nLink (tap to copy):\n<code>{link}</code>',parse_mode="HTML",reply_markup=user_keyboards.get_beat_kb(product_id))

@router.message(F.text == "🌏 Sell Beats")
async def seller_handler(message: Message, is_clb=False, **kwargs):
    await message.answer(text='Seller Welcome MSG', reply_markup=user_keyboards.get_main_seller_kb())

@router.message(F.text == "🌏 Buy Beats")
async def buyer_handler(message: Message, is_clb=False, **kwargs):
    await start_handler(message)


