
import aiosqlite,aiofiles
from typing import Any,Optional

DB_PATH = "src/databases/licenses.db"
class LicensesDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS licenses(
                                    license_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    user_id INTEGER,
                                    name STRING,
                                    description STRING,
                                    price STRING,
                                    feature INTEGER,
                                    license_type INTEGER,
                                    min_offer_price REAL,
                                    markdown_template int,
                                    is_archived INTEGER,
                                    is_offer_only INTEGER,
                                    is_active INTEGER
                                    )'''
                                  ) as cursor:
                pass

    @classmethod
    async def get_value(cls, key: Any, license_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT {key} FROM licenses WHERE license_id = {license_id}') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]

    @classmethod
    async def get_licenses_by_user(
        cls, 
        user_id: int, 
        license_type: int | None = 5, 
        active_only: int | None = 1
    ) -> list:
        async with aiosqlite.connect(DB_PATH) as db:
            query = 'SELECT * FROM licenses WHERE user_id = ? AND license_type <= ?'
            params = [user_id, license_type]

            if active_only == 1:
                query += ' AND is_active = 1'

            async with db.execute(query, params) as cursor:
                result = await cursor.fetchall()
                
                return result if result else []

    
    @classmethod
    async def get_license(cls, license_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('SELECT * FROM licenses WHERE license_id = ?', (license_id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:  # Проверяем, если результата нет
                    return None  # Или можно выбросить исключение, если это предпочтительно
                return result

            
    @classmethod    
    async def get_feature_by_user(cls, user_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT price FROM licenses WHERE user_id = {user_id} AND feature = 1') as cursor:
                result = await cursor.fetchone()
                if not result:
                    return -1
                return result[0]
            
    @classmethod
    async def get_all(cls):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT * FROM licenses') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result

    # @classmethod
    # async def get_product(cls, product_id: int):
    #     async with aiosqlite.connect(DB_PATH) as db:
    #         async with db.execute(f'SELECT * FROM licenses WHERE product_id = {product_id}') as cursor:
    #             result = await cursor.fetchone()
    #             if not result:
    #                 return -1
    #             return result
            

    @classmethod
    async def set_value(cls, license_id: int, key: Any, new_value: Any):
        async with aiosqlite.connect(DB_PATH) as db:
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
                            license_type:int|None = 0,
                            min_offer_price: float| None = None,
                            license_file: str | None = None,
                            is_archived:int| None = 0,
                            is_offer_only:int| None = 0,
                            is_active:int| None = 0,
                            ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'INSERT INTO licenses ("user_id", "name", "description", "price", "feature","license_type", "min_offer_price","license_file","is_archived","is_offer_only","is_active") VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                             (user_id,name,description,price,feature,license_type,min_offer_price,license_file,is_archived,is_offer_only,is_active))
            await db.commit()
    

    @classmethod
    async def del_license(cls,license_id):        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM licenses WHERE license_id = {license_id}')
            await db.commit()
    
    @classmethod
    async def del_all_by_user(cls,user_id):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM licenses WHERE user_id = {user_id}')
            await db.commit()
    
    @classmethod
    async def toggle_license_active(cls, license_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            # Получаем данные лицензии по license_id
            license_row = await cls.get_license(license_id)

            # Проверяем все элементы кроме седьмого (оффер под будущее)
            check_elements = license_row[:6] + license_row[8:]

            if all(value is not None for value in check_elements):  # Пропускаем user_id
                current_active_status = license_row[11]  # Поле is_active (11 - индекс, если counting starts from 0)
                new_active_status = 0 if current_active_status == 1 else 1
                
                # Используем метод set_value для обновления значения is_active
                await cls.set_value(license_id=license_id, key='is_active', new_value=new_active_status)
                return new_active_status  # Возвращаем новое состояние is_active
            else:
                return -1
            
    @classmethod
    async def set_featured_license(cls, user_id: int, license_id: int):
        async with aiosqlite.connect(DB_PATH) as db:
            # Сначала снимем статус избранной лицензии с других лицензий
            await db.execute(
                'UPDATE licenses SET feature = 0 WHERE user_id = ? AND feature = 1',
                (user_id,)
            )

            # Теперь установим новую лицензию как избранную
            await db.execute(
                'UPDATE licenses SET feature = 1 WHERE license_id = ?',
                (license_id,)
            )

            await db.commit()




    @classmethod
    async def set_default(cls, user_id:int):
        await cls.create_table()
        await cls.del_all_by_user(user_id=user_id)
        await cls.create_license(user_id=user_id,name="Mp3 Lease",description='MP3',price=20,feature=1,license_type=1,license_file=None,is_active=1,)
        await cls.create_license(user_id=user_id,name="Wav Lease",description='MP3 + WAV',price=30,feature=0,license_type=2,license_file=None,is_active=1,)
        await cls.create_license(user_id=user_id,name="Stems Lease",description='MP3 + WAV + STEMS',price=60,feature=0,license_type=3,license_file=None,is_active=1,)
        await cls.create_license(user_id=user_id,name="Unlimited",description='MP3 + WAV + STEMS',price=100,feature=0,license_type=4,license_file=None,is_active=1,)
        await cls.create_license(user_id=user_id,name="Exclusive",description='MP3 + WAV + STEMS',price=250,feature=0,license_type=5,license_file=None,is_active=1,)


class LicensesProductsDatabase:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS products(
                                    product_id INTEGER,
                                    license_id INTEGER,
                                    disabled INTEGER,
                                    custom_price INTEGER
                                  )'''
                                  ) as cursor:
                pass
    
    @classmethod
    async def set_value(cls, id: int, key: Any, new_value: Any):
        async with aiosqlite.connect(DB_PATH) as db:
            if type(key) is int:
                await db.execute(f'UPDATE products SET {key}={new_value} WHERE id={id}')
            else:
                await db.execute(f'UPDATE products SET {key}=? WHERE id={id}',(new_value,))
            await db.commit()

    @classmethod
    async def create(cls, 
                        product_id: int,
                        license_id:int,
                        disabled:int |None = 1,
                        custom_price: float | None = None,
                       ):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'INSERT INTO products ("product_id", "license_id", "disabled","custom_price") VALUES (?,?,?,?)',
                             (product_id,license_id,disabled, custom_price))
            await db.commit()
    @classmethod
    async def get_disabled(cls, product_id:int):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f'SELECT license_id FROM products WHERE product_id = {product_id} AND disabled = 1') as cursor:
                result = await cursor.fetchall()
                if not result:
                    return []
                return result
    @classmethod
    async def del_row(cls,license_id:int,product_id:int):        
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(f'DELETE FROM products WHERE license_id = {license_id} AND product_id = {product_id}')
            await db.commit()
   
class LicenseTemplates:

    @classmethod
    async def create_table(self):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute('''CREATE TABLE IF NOT EXISTS templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный идентификатор шаблона
    license_id INTEGER DEFAULT NULL,       -- ID лицензии (NULL для дефолтного шаблона)
    markdown TEXT NOT NULL,                -- Шаблон договора в формате Markdown
    UNIQUE (license_id),                   -- Один шаблон на одну лицензию
    FOREIGN KEY (license_id) REFERENCES licenses(id) ON DELETE CASCADE);'''
                                  ) as cursor:
                pass
    
    @classmethod
    async def upsert_template(cls, markdown: str,license_id: Optional[int] = None,) -> None:
        """
        Вставка или обновление шаблона.
        Если markdown совпадает с дефолтным, связываем license_id с дефолтным шаблоном.
        :param license_id: ID лицензии (None для дефолтного шаблона)
        :param markdown: Текст шаблона в формате Markdown
        """
        async with aiosqlite.connect(DB_PATH) as db:
            # Попытка вставить дефолтный шаблон
            insert_default_query = '''
            INSERT OR IGNORE INTO templates (markdown)
            VALUES (?)
            '''
            cursor = await db.execute(insert_default_query, (markdown,))
            template_id = cursor.lastrowid

            # Если добавлена новая запись с license_id=NULL
            if template_id == 0 :
                return 
                
            
            # Если указано license_id, обновляем её в дефолтной записи
            if license_id is not None:
                # Обновляем license_id в дефолтной записи
                update_license_query = '''
                UPDATE templates
                SET license_id = ?
                WHERE template_id = ? AND license_id IS NULL
                '''
                await db.execute(update_license_query, (license_id, template_id))

                # Удаляем другие записи с этим license_id
                delete_other_query = '''
                DELETE FROM templates
                WHERE license_id = ? AND template_id != ?
                '''
                await db.execute(delete_other_query, (license_id, template_id))

    
    @classmethod
    async def initialize_default_markdown(cls):
        async with aiofiles.open("src/default_markdown.md", mode="r", encoding="utf-8") as f:
                default_markdown = await f.read()
                await cls.upsert_template(markdown=default_markdown)
    
    @classmethod
    async def get_markdown(cls,license_id) -> str:         
           async with aiosqlite.connect(DB_PATH) as db:
                cursor = await db.execute('SELECT markdown FROM templates WHERE license_id IS NULL LIMIT 1')
                row = await cursor.fetchone()
                return row[0] if row else '' 
        

