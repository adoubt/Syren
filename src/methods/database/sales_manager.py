import aiosqlite
from typing import Any
from datetime import datetime

class SalesDatabase:



    # async def __aiter__(self):
    #     return await self.__wrapped__.__aiter__()

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/sales.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS sales(
                                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    customer_id INTEGER,
                                    seller_id INTEGER,
                                    products_id INTEGER,
                                    total_amount REAL,
                                    currency STRING,
                                    discount REAL,
                                    service_fee,
                                    license_file STRING,
                                    promo_code_id INTEGER,
                                    offer_id INTEGER,
                                    datetime INTEGER,
                                    invoice STRING,
                                    payment_method STRING)'''
                                  ) as cursor:
                pass
    
    @classmethod
    async def create_sale(cls,
                            customer_id :int,
                            seller_id :int,
                            products_id :int,
                            total_amount :float,
                            currency :str,
                            discount: float,
                            service_fee : float,
                            license_file :str,
                            promo_code_id :int,
                            invoice :str,
                            payment_method :str,
                            offer_id :int |None = None):
    
        current_datetime = int(datetime.timestamp(datetime.now()))
        async with aiosqlite.connect("src/databases/sales.db") as db:
            await db.execute(f'INSERT INTO sales("customer_id", "seller_id", "products_id", "total_amount", "currency","discount","service_fee","license_file","promo_code_id","offer_id","datetime","invoice","payment_method") VALUES  (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             (customer_id, seller_id, products_id, total_amount, currency,discount,service_fee,license_file,promo_code_id,offer_id,current_datetime,invoice,payment_method))
            await db.commit()

    @classmethod
    async def get_value(cls, key: Any, sale_id:int):
        async with aiosqlite.connect("src/databases/sales.db") as db:
            async with db.execute(f'SELECT {key} FROM sales WHERE sale_id = {sale_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def set_value(cls, sale_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/sales.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE sales SET {key}={new_value} WHERE sale_id={sale_id}')
            else:
                await db.execute(f'UPDATE sales SET {key}=? WHERE sale_id={sale_id}',(new_value,))
            await db.commit()

    @classmethod
    async def get_sale(cls,sale_id: int):
        async with aiosqlite.connect("src/databases/sales.db") as db:
            async with db.execute(f'SELECT * FROM sales WHERE sale_id = {sale_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
        
    # classmethod    
    # async def get_sale_by_user(cls, user_id:int):
    #     async with aiosqlite.connect("src/databases/carts.db") as db:
    #         async with db.execute(f'SELECT * FROM carts WHERE user_id = {user_id}') as cursor:
    #             result = await cursor.fetchall()
    #             if not result:
    #                 return []
    #             return result
            

