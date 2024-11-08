import aiosqlite
from typing import Any


class WishlistsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS wishlists(
                                    user_id INTEGER PRIMARY KEY,
                                    product_id INTEGER,
                                    license_id INTEGER
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, user_id:int):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            async with db.execute(f'SELECT {key} FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            
    @classmethod
    async def get_wishlist_count(cls, user_id:int):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            async with db.execute(f'SELECT COUNT(*) FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod        
    async def del_from_wishlist(cls,user_id:int,product_id:int):        
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            await db.execute(f'DELETE FROM wishlists WHERE user_id = {user_id} and product_id = {product_id}')
            await db.commit()
    
    @classmethod
    async def empty_wishlist(cls, user_id):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            await db.execute(f'DELETE FROM wishlists WHERE user_id = {user_id}')
            await db.commit()
    
    @classmethod # When the beat was sold exclusively
    async def del_product_from_wishlists(cls, product_id):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            await db.execute(f'DELETE FROM wishlists WHERE product_id = {product_id}')
            await db.commit()

    @classmethod
    async def add_to_wishlist(cls, 
                            user_id: int,
                            product_id: int,
                            license_id: int
                            ):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            await db.execute(f'REPLACE INTO wishlists ("user_id", "product_id","license_id") VALUES (?,?,?)',
                             (user_id,product_id,license_id))
            await db.commit()
    
    @classmethod    
    async def get_wishlist_by_user(cls, user_id:int):
        async with aiosqlite.connect("src/databases/wishlists.db") as db:
            async with db.execute(f'SELECT * FROM wishlists WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result