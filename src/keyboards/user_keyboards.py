from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_choose_licenses_kb(beat_id,) -> InlineKeyboardMarkup:

    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='mp3 5 руб', callback_data=f'addToCart_{beat_id}_{license_id}')],
        [InlineKeyboardButton(text='wav 10 руб', callback_data='vvv')]
        
    ]) 
    return ikb

def get_showcase_kb (feature_license: int| None) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Buy {feature_license}', callback_data='choose_license')],
    ]) 
    return ikb