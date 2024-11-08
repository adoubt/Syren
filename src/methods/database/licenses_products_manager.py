
import aiosqlite
from typing import Any

class LicensesProductsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/licenses_products.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS licenses_products(
                                    product_id INTEGER,
                                    license_id INTEGER,
                                    disabled INTEGER,
                                    custom_price INTEGER
                                  )'''
                                  ) as cursor:
                pass
    
    @classmethod
    async def set_value(cls, id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/licenses_products.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE licenses_products SET {key}={new_value} WHERE id={id}')
            else:
                await db.execute(f'UPDATE licenses_products SET {key}=? WHERE id={id}',(new_value,))
            await db.commit()

    @classmethod
    async def create(cls, 
                        product_id: int,
                        license_id:int,
                        disabled:int |None = 1,
                        custom_price: float | None = None,
                       ):
        async with aiosqlite.connect("src/databases/licenses_products.db") as db:
            await db.execute(f'INSERT INTO licenses_products ("product_id", "license_id", "disabled","custom_price") VALUES (?,?,?,?)',
                             (product_id,license_id,disabled, custom_price))
            await db.commit()
    @classmethod
    async def get_disabled(cls, product_id:int):
        async with aiosqlite.connect("src/databases/licenses_products.db") as db:
            async with db.execute(f'SELECT license_id FROM licenses_products WHERE product_id = {product_id} AND disabled = 1') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    @classmethod
    async def del_row(cls,license_id:int,product_id:int):        
        async with aiosqlite.connect("src/databases/licenses_products.db") as db:
            await db.execute(f'DELETE FROM licenses_products WHERE license_id = {license_id} AND product_id = {product_id}')
            await db.commit()
   
    

