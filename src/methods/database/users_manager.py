import aiosqlite
from typing import Any

class UsersDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(
                    f'''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY,
                                                        is_seller INTEGER,
                                                        is_banned INTEGER,
                                                        is_admin INTEGER,
                                                        balance REAL,
                                                        username STRING,
                                                        artist_name STRING,
                                                        email STRING,
                                                        insta STRING,
                                                        subscription INTEGER,
                                                        wallet INTEGER,
                                                        language STRING)''') as cursor:
                pass

    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_all_banned(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE is_banned=1') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    @classmethod
    async def get_user(cls, user_id: int):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT * FROM users WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def create_user(cls, user_id: int,language:str|None = "ENG"):
        async with aiosqlite.connect("src/databases/users.db") as db:
            await db.execute(f'''INSERT INTO users("user_id", "is_seller", "is_banned", "is_admin", "balance","username","artist_name", "email","insta","subscription", "wallet", "language") 
                             VALUES ({user_id}, 0, 0, 0, 0, "durov", "Travis Scott", "ab@somegoogle.com",'', 0, 0,"ENG")''')
            await db.commit()

    @classmethod
    async def get_value(cls, user_id: int, key: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            async with db.execute(f'SELECT {key} FROM users WHERE user_id = {user_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def set_value(cls, user_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect("src/databases/users.db") as db:
            if type(key) is int:
                await db.execute(f'UPDATE users SET {key}={new_value} WHERE user_id={user_id}')
            else:
                await db.execute(f'UPDATE users SET {key}=? WHERE user_id={user_id}',(new_value,))
            await db.commit()

    # @classmethod        
    # async def clear_all_context(cls):
    #     async with aiosqlite.connect("src/databases/users.db") as db:
            
    #         await db.execute(f'UPDATE users SET context=""')
    #         await db.commit()
    # @classmethod        
    # async def clear_context(cls,user_id:int):
    #     async with aiosqlite.connect("src/databases/users.db") as db:
            
    #         await db.execute(f'UPDATE users SET context="" WHERE user_id ={user_id}')
    #         await db.commit()


    @classmethod        
    async def del_users(cls):
        async with aiosqlite.connect("src/databases/users.db") as db:
            
            await db.execute(f'DELETE from users')
            await db.commit()

    @classmethod
    async def add_points(cls, user_id: int, points: int):
        await cls.set_value(user_id, 'balance', (await cls.get_value(user_id, 'balance')) + points)
    
    # @classmethod
    # async def add_requets(cls, user_id: int, requests: int):
    #     await cls.set_value(user_id, 'requests_left', (await cls.get_value(user_id, 'requests_left')) + requests)
    
    @classmethod
    async def is_banned(cls, user_id: int):
        return await cls.get_value(user_id, 'is_banned')

    @classmethod
    async def is_admin(cls, user_id: int):
        return (await cls.get_value(user_id, 'status')) == 1
    
    
# INSERT INTO users("user_id", "balance", "is_banned", "status", "context") VALUES ({user_id}, 0, 0, 0, "")'
# 'CREATE TABLE prompts(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT, body TEXT)')