
import aiosqlite
from typing import Any


class ProductsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/products.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS products(
                                    beat_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    user_id INTEGER,
                                    name STRING,
                                    bpm INTEGER,
                                    preview_link STRING,
                                    mp3_link STRING,
                                    wav_link STRING,
                                    stems_link STRING,
                                    image_link STRING,
                                    is_sold INTEGER,
                                    views INTEGER,
                                    collab STRING,
                                    tags STRING,
                                    genre STRING,
                                    mood STRING,
                                    date STRING,
                                    title STRING,
                                    performer STRING
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, beat_id:int):
        async with aiosqlite.connect("src/databases/products.db") as db:
            async with db.execute(f'SELECT {key} FROM products WHERE beat_id = {beat_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/products.db") as db:
            async with db.execute(f'SELECT * FROM products') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_product(cls, beat_id: int):
        async with aiosqlite.connect("src/databases/products.db") as db:
            async with db.execute(f'SELECT * FROM products WHERE beat_id = {beat_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result
            

    @classmethod
    async def set_value(cls, beat_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/productss.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE products SET {key}={new_value} WHERE beat_id={beat_id}')
            else:
                await db.execute(f'UPDATE products SET {key}=? WHERE beat_id={beat_id}',(new_value,))
            await db.commit()

    @classmethod
    async def create_product(cls, 
                            user_id: int,
                            name: str,
                            bpm: int | None = 0,
                            preview_link: str | None='',
                            mp3_link: str | None='',
                            wav_link: str | None='',
                            stems_link: str | None='',
                            image_link: str | None='',
                            is_sold: int | None = 0,
                            views: int | None = 0,
                            collab: int | None = 0,
                            tags: str | None='',
                            genre: str | None='',
                            mood: str | None='',
                            date: str | None='',
                            title: str | None='', 
                            performer: str | None='',
                            ):
        async with aiosqlite.connect("src/databases/products.db") as db:
            await db.execute(f'INSERT INTO products ("user_id", "name", "bpm", "preview_link", "mp3_link","wav_link","stems_link", "image_link","is_sold", "views","collab","tags","genre","mood","date","title","performer") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             (user_id,name,bpm,preview_link,mp3_link,wav_link,stems_link,image_link,is_sold,views,collab,tags,genre,mood,date,title,performer))
            await db.commit()
#INSERT INTO products ("name", "requests", "price_usd", "price_rub", "short_desc", "long_desc") VALUES ("50 Запросов 📕" ,100,1.00,49, "50 Запросов за 49 Рублей","Вы получите 50 запросов для общения с ботом. Запросом может быть как обычное сообщение, так и фото!")
#INSERT INTO products ("name", "requests", "price_usd", "price_rub", "short_desc", "long_desc") VALUES ("200 Запросов 📚" ,200,3.00,149, "200 Запросов за 149 Рублей","Вы получите 200 запросов для общения с ботом. Запросом может быть как обычное сообщение, так и фото!")
  
    @classmethod
    async def del_products(cls):
        async with aiosqlite.connect("src/databases/products.db") as db:
            await db.execute(f'DELETE FROM products')
            await db.commit()
    @classmethod
    async def del_product(cls,beat_id):        
        async with aiosqlite.connect("src/databases/products.db") as db:
            await db.execute(f'DELETE FROM products WHERE beat_id = {beat_id}')
            await db.commit()