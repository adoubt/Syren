from aiogram import Router
from src.misc import bot,cp

router = Router()

# Обработчик создания счета
@router.message()
async def get_invoice(message):
    invoice = await cp.create_invoice(1, "USDT")  # Создаем счет на 1 USDT
    await message.answer(f"Pay here: {invoice.bot_invoice_url}")
    invoice.await_payment(message=message)  # Ждем оплаты

# Обработчик успешной оплаты
@cp.polling_handler()
async def handle_payment(invoice, message):
    await message.answer(f"Invoice #{invoice.invoice_id} has been paid")

#