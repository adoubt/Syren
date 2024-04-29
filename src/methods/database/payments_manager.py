import aiosqlite
from typing import Any
from datetime import datetime

class OrdersDatabase:



    # async def __aiter__(self):
    #     return await self.__wrapped__.__aiter__()

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS orders(
                                    id STRING PRIMARY KEY,
                                    pay_link STRING,
                                    user_id INTEGER,
                                    product_id INTEGER,
                                    status INTEGER,
                                    datetime INTEGER,
                                    method STRING)'''
                                  ) as cursor:
                pass
    
    @classmethod
    async def create_order(cls,
                            order_id: str,
                            pay_link: str,
                            user_id: int,
                            product_id: int,
                            method:str,
                            status:int|None = 0):
    
        current_datetime = int(datetime.timestamp(datetime.now()))
        async with aiosqlite.connect("src/databases/payments.db") as db:
            await db.execute(f'INSERT INTO orders("id", "pay_link", "user_id", "product_id", "status","datetime","method") VALUES  (?,?,?,?,?,?,?)',(order_id,pay_link,user_id,product_id,status,current_datetime,method))
            await db.commit()

    @classmethod
    async def get_value(cls, key: Any, order_id:str):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(f'SELECT {key} FROM orders WHERE id = {order_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def get_pending_orders(cls) -> dict:
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(f'SELECT * FROM orders WHERE status = 0') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    
    @classmethod
    async def get_pending_orders_by_user(cls,user_id:int)->dict:
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(f'SELECT * FROM orders WHERE (status = 0 AND user_id = {user_id})') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    @classmethod
    async def set_value(cls, order_id: str, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE orders SET {key}={new_value} WHERE id={order_id}')
            else:
                await db.execute(f'UPDATE orders SET {key}=? WHERE id={order_id}',(new_value,))
            await db.commit()

    @classmethod
    async def delete_pending_orders_by_user(cls,user_id:int):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            await db.execute(f'DELETE FROM orders WHERE (user_id = {user_id} AND status = 0)')
            await db.commit()

    @classmethod
    async def get_pending_order_by_user(cls,user_id:int):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(f'SELECT id FROM orders WHERE(user_id = {user_id} AND status = 0)') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            

######### НЕ ЮЗАЕТСЯ #########

class PendingStatus:

    
    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(
                    f'CREATE TABLE IF NOT EXISTS statuses(id INTEGER PRIMARY KEY, discription STRING)') as cursor:
                pass
            
class PaymentsMethod:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/payments.db") as db:
            async with db.execute(
                    f'CREATE TABLE IF NOT EXISTS methods(name STRING PRIMARY KEY, discription STRING)') as cursor:
                pass
    