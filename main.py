import asyncio
from loguru import logger

from src.handlers import user_handler, cryptopay_handler

from src.misc import bot, dp, cp
# from src.methods.payment import payment_checker


def register_handlers():
    dp.include_routers(user_handler.router)
    dp.include_routers(cryptopay_handler.router)  # Регистрация CryptoPay обработчиков

# Платежный поток (можно временно отключить)
async def payment_polling():
    # await payment_checker.run_order_status_checker()  # Оставь, если нужно
    pass


async def main():
    register_handlers()
    # aaio_polling_task = asyncio.create_task(payment_polling())  # Отключено, если не нужно
    await asyncio.gather(
        dp.start_polling(bot),  # Telegram-бот
        cp.run_polling(),       # CryptoPay
        # aaio_polling_task      # Закомментировано для исключения третьего потока
    )

if __name__ == "__main__":
    logger.add('src/logs/logs.log', format="{time} {level} {message}", level='DEBUG')   

    asyncio.run(main())