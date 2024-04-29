
import aiosqlite
from typing import Any


class LicensesDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS licenses(
                                    license_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    user_id INTEGER,
                                    name STRING,
                                    description STRING,
                                    price STRING,
                                    feature INTEGER,
                                    mp3 INTEGER,
                                    wav INTEGER,
                                    stems INTEGER,
                                    is_exclusive INTEGER,
                                    min_offer_price REAL,
                                    license_file STRING,
                                    is_archived STRING,
                                    is_offer_only INTEGER
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, license_id:int):
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            async with db.execute(f'SELECT {key} FROM licenses WHERE license_id = {license_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
    
    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            async with db.execute(f'SELECT * FROM licenses') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    # @classmethod
    # async def get_product(cls, product_id: int):
    #     async with aiosqlite.connect("src/databases/licenses.db") as db:
    #         async with db.execute(f'SELECT * FROM licenses WHERE product_id = {product_id}') as cursor:
    #             result = await cursor.fetchone()
    #             if not result:
    #                 return -1
    #             return result
            

    @classmethod
    async def set_value(cls, license_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/licensess.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE licenses SET {key}={new_value} WHERE license_id={license_id}')
            else:
                await db.execute(f'UPDATE licenses SET {key}=? WHERE license_id={license_id}',(new_value,))
            await db.commit()

    @classmethod
    async def create_license(cls, 
                            user_id: int,
                            name: str| None = 'new license',
                            description: str| None = '',
                            price: float | None = None,
                            feature: int| None = 0,
                            mp3: int| None = 0,
                            wav: int| None = 0,
                            stems: int| None = 0,
                            is_exclusive: int| None = 0,
                            min_offer_price: float| None = None,
                            license_file: str | None = None,
                            is_archived:int| None = 0,
                            is_offer_only:int| None = 0,
                            ):
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            await db.execute(f'INSERT INTO licenses ("user_id", "name", "description", "price", "feature","mp3","wav", "stems","is_exclusive", "min_offer_price","license_file","is_archived","is_offer_only") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                             (user_id,name,description,price,feature,mp3,wav,stems,is_exclusive,min_offer_price,license_file,is_archived,is_offer_only))
            await db.commit()
    
#INSERT INTO licenses ("name", "requests", "price_usd", "price_rub", "short_desc", "long_desc") VALUES ("50 Запросов 📕" ,100,1.00,49, "50 Запросов за 49 Рублей","Вы получите 50 запросов для общения с ботом. Запросом может быть как обычное сообщение, так и фото!")
#INSERT INTO licenses ("name", "requests", "price_usd", "price_rub", "short_desc", "long_desc") VALUES ("200 Запросов 📚" ,200,3.00,149, "200 Запросов за 149 Рублей","Вы получите 200 запросов для общения с ботом. Запросом может быть как обычное сообщение, так и фото!")
  
   
    async def del_license(cls,license_id):        
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            await db.execute(f'DELETE FROM licenses WHERE license_id = {license_id}')
            await db.commit()

    async def del_all_by_user(cls, user_id):
        async with aiosqlite.connect("src/databases/licenses.db") as db:
            await db.execute(f'DELETE FROM licenses WHERE user_id = {user_id}')
            await db.commit()




    @classmethod
    async def set_default(cls, user_id:int):
        await cls.create_table()
        await cls.create_license(user_id=user_id,name="Mp3 Lease",description='MP3',price=20,feature=1,mp3=1,license_file='file_id contract',)
        await cls.create_license(user_id=user_id,name="Wav Lease",description='MP3 + WAV',price=35,feature=0,mp3=1,wav=1,license_file='file_id contract',)
        await cls.create_license(user_id=user_id,name="Stems Lease",description='MP3 + WAV + STEMS',price=75,feature=0,mp3=1,wav=1,stems=1,license_file='file_id contract',)
        await cls.create_license(user_id=user_id,name="Unlimited",description='MP3 + WAV + STEMS',price=150,feature=0,mp3=1,wav=1,stems=1,license_file='file_id contract',)
        await cls.create_license(user_id=user_id,name="Exclusive",description='MP3 + WAV + STEMS',price=500,feature=0,mp3=1,wav=1,stems=1,is_exclusive=1,license_file='file_id contract',)
        