import asyncio
from loguru import logger
from src.handlers import user_handler
from src.misc import bot, dp
from src.methods.payment import payment_checker

def register_handlers():
    dp.include_routers(user_handler.router)

async def payment_polling():
    await payment_checker.run_order_status_checker()

async def main():
    register_handlers()
    # Создание задачи для асинхронного потока
    aaio_polling_task = asyncio.create_task(payment_polling())
    await dp.start_polling(bot)
    # Ожидание завершения асинхронного потока
    await aaio_polling_task

if __name__ == "__main__":
    logger.add('src/logs/logs.log', format="{time} {level} {message}", level='DEBUG')   

    asyncio.run(main())