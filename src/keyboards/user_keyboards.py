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
   

def get_showcase_kb(product_id:int, price,is_sold:int, license_type:int,channel: str) -> InlineKeyboardMarkup:

    
    channel_btn = [InlineKeyboardButton(text=f'Channel', url='https://t.me/Noreason4l')]
    if is_sold == 0:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'from {price} USD', callback_data=f'choose_license_{product_id}')],
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
        [InlineKeyboardButton(text=cart_view, callback_data='open_cart')],
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