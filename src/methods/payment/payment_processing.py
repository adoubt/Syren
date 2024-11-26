from src.methods.database.users_manager import UsersDatabase
from src.methods.database.products_manager import ProductsDatabase
from methods.database.orders_manager import OrdersDatabase
from loguru import logger
from src.misc import bot

class ProcessOrder:



    @classmethod 
    async def success_order(cls,user_id:int,product_id:int,order_id:str):
        status = 1
        logger.success(f"Order {order_id} оплачен! (ID юзера: {user_id}")

        await cls.close_order(order_id,status)
        await cls.add_product_to_user_account(user_id,product_id)
        await cls.notificate_user(user_id,order_id,status) 
    
    @classmethod
    async def expired_order(cls,user_id:int, order_id:str):
        status = 2
        logger.info(f"Order {order_id} expired! (ID юзера: {user_id}")

        await cls.close_order(order_id,status)   
        await cls.notificate_user(user_id,order_id,status)

    @classmethod
    async def cancel_orders(cls,user_id:int):
        order_id = await OrdersDatabase.get_pending_order_by_user(user_id)
        if order_id == -1:
            return
        
        status = 3
        logger.info(f"Order {order_id} отменен! (ID юзера: {user_id})")
        await cls.close_order(order_id,status)   
        await cls.notificate_user(user_id,order_id,status)
        
        #Если будут баги с несколькими открытми ордерами
        # await OrdersDatabase.delete_pending_orders_by_user


    @classmethod
    async def close_order(cls,order_id:str,status:int):
        await OrdersDatabase.set_value(order_id=order_id,key='status',new_value=status)

    @classmethod
    async def notificate_user(cls,user_id:int,order_id:str,status:int):

        if status == 1:
            text = f'Оплата заказа #<code>{order_id}</code> прошла успешно!\nСпасибо за покупку🤝'  
        elif status == 2:
            text = f'Заказ #<code>{order_id}</code> отменен.\nВышло время ожидания оплаты ⌛️'
        elif status == 3:
            text = f'Заказ #<code>{order_id}</code> отменен.'
        try:
            await bot.send_message(chat_id=user_id,text=text,parse_mode='HTML')
        except Exception as e:
            logger.error(f'Ошибка при отправке уведомления о статусе заказа(order_id:{order_id} user_id:{user_id}). Error: {e}')
    
    
    @classmethod  # Сабмит гудсов юзеру 
    async def add_product_to_user_account(cls,user_id,product_id):
        requests = await ProductsDatabase.get_value(key='requests',id=product_id)
        await UsersDatabase.add_requets(user_id,requests)