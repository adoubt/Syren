from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_licenses_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='mp3 5 руб', callback_data='AAA')],
        [InlineKeyboardButton(text='wav 10 руб', callback_data='vvv')]
        
    ]) 
    return ikb