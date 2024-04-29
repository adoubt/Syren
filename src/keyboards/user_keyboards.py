from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_choose_licenses_kb(product_id,user_licenses) -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='mp3 5 руб', callback_data=f'addToCart_{product_id}_{license_id}')],
        [InlineKeyboardButton(text='wav 10 руб', callback_data='vvv')]
        
    ]) 
    return ikb

def get_showcase_kb(price: int| None,channel: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'from{price}', callback_data='choose_license')],
        [InlineKeyboardButton(text=f'Channel', url='https://t.me/Noreason4l')],
    ]) 
    return ikb

def get_homepage_kb(cart)-> InlineKeyboardMarkup:
    cart_view = 'Cart'
    if cart > 0:cart_view = f'Cart({cart})'
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cart_view, callback_data='open_cart')],
    ]) 
    return ikb

def get_settings_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сменить язык", callback_data='change_languge')],
        [InlineKeyboardButton(text="Уведомления", callback_data='notifications')],
        [InlineKeyboardButton(text="Назад", callback_data='homepage')],
    ]) 
    return ikb