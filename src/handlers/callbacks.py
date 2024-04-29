import user_handler
from user_handler import router
from aiogram.types import CallbackQuery
from decorators import new_user_handler,new_seller_handler


@router.callback_query(lambda clb: clb.data == 'start')
@new_user_handler
async def start_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await user_handler.start_handler(clb.message, is_clb=True)

@router.callback_query(lambda clb: clb.data == 'homepage')
@new_user_handler
async def homepage_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await user_handler.homepage_handler(clb.message, is_clb=True)


@router.callback_query(lambda clb: clb.data == 'settings')
@new_user_handler
async def settings_clb_handler(clb: CallbackQuery, is_clb=False, **kwargs):
    await user_handler.settings_handler(clb.message, is_clb=True)