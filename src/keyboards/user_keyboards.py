from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_choose_licenses_kb(user_id,product_id,licenses) -> InlineKeyboardMarkup:
    buttons = []
    for license in licenses: 
         buttons = buttons+[InlineKeyboardButton(text=f'{license[2]} | {license[4]} USD', callback_data=f"addToCart_{product_id}_{license[0]}_{user_id}")]
    
    back = []
    back.append(InlineKeyboardButton(text='Назад', callback_data=f"showcase_{product_id}")) 
    rows= [[btn] for btn in buttons] + [back]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb   
   

def get_showcase_kb(product_id:int, is_sold:int, channel:str, already_in_cart:int,price:int| None = None) -> InlineKeyboardMarkup:
    if already_in_cart ==1:
        cart_btn = [InlineKeyboardButton(text=f'Go To Cart', callback_data='cart')]
    else:
        cart_btn = [InlineKeyboardButton(text=f'from {price} USD', callback_data=f'choose_license_{product_id}')]
    channel_btn = [InlineKeyboardButton(text=f'Channel', url=channel)]
    if is_sold == 0:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
        cart_btn,
        channel_btn,
        ]) 
    else:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
        channel_btn,
    ]) 
    return ikb

def get_homepage_kb(user_id, cart)-> InlineKeyboardMarkup:
    cart_view = 'Cart'
    if cart > 0:cart_view = f'Cart({cart})'
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cart_view, callback_data='cart')],
        [InlineKeyboardButton(text='Settings', callback_data='settings')]
    ]) 
    return ikb

def get_settings_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сменить язык", callback_data='change_languge')],
        [InlineKeyboardButton(text="Уведомления", callback_data='notifications')],
        [InlineKeyboardButton(text="Назад", callback_data='homepage')],
    ]) 
    return ikb

def get_item_in_cart_kb(user_id,product_id,license_name,price,description, license_file)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Pay {price} USD", callback_data=f'Pay_{user_id}_{product_id}')],
        [InlineKeyboardButton(text="Remove❌", callback_data=f'delItemFromCart_{user_id}_{product_id}')],
    ]) 
    return ikb
# def get_total_in_cart_kb()

