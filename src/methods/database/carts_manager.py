import aiosqlite
from typing import Any


class CartsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/carts.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS catrs(
                                    user_id INTEGER PRIMARY KEY,
                                    product_id INTEGER,
                                    license_id INTEGER
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, user_id:int):
        async with aiosqlite.connect("src/databases/carts.db") as db:
            async with db.execute(f'SELECT {key} FROM carts WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod        
    async def del_from_cart(cls,user_id:int,product_id:int):        
        async with aiosqlite.connect("src/databases/carts.db") as db:
            await db.execute(f'DELETE FROM carts WHERE user_id = {user_id} and product_id = {product_id}')
            await db.commit()
    
    @classmethod
    async def empty_cart(cls, user_id):
        async with aiosqlite.connect("src/databases/carts.db") as db:
            await db.execute(f'DELETE FROM carts WHERE user_id = {user_id}')
            await db.commit()
    
    @classmethod # When the beat was sold exclusively
    async def del_product_from_carts(cls, product_id):
        async with aiosqlite.connect("src/databases/carts.db") as db:
            await db.execute(f'DELETE FROM carts WHERE product_id = {product_id}')
            await db.commit()

    @classmethod
    async def add_to_cart(cls, 
                            user_id: int,
                            product_id: int,
                            license_id: int,
                            ):
        async with aiosqlite.connect("src/databases/carts.db") as db:
            await db.execute(f'INSERT INTO carts ("user_id", "product_id","license_id") VALUES (?,?,?)',
                             (user_id,product_id,license_id))
            await db.commit()