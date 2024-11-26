import aiosqlite, asyncio
from typing import List, Tuple, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass


@dataclass
class Cart:
    cart_id: int
    user_id: int
    status: str
    created_at: int
    updated_at: int


@dataclass
class CartItem:
    cart_item_id: int
    cart_id: int
    product_id: int
    quantity: int
    license_id: int
    added_at: int


class Database:
    """Асинхронный класс для работы с базой данных."""

    def __init__(self, db_path: str = "src/databases/carts.db"):
        self.db_path = db_path
    
    @asynccontextmanager
    async def get_db_connection(self):
        """Асинхронный контекстный менеджер для работы с базой данных."""
        db = await aiosqlite.connect(self.db_path)
        try:
            yield db
        finally:
            await db.commit()
            await db.close()

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Выполнение запроса без возврата значений."""
        async with self.get_db_connection() as db:
            await db.execute(query, params)

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Tuple]:
        """Получить одну запись."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple = ()) -> List[Tuple]:
        """Получить все записи."""
        async with self.get_db_connection() as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()
    async def create_tables(self): 
        """Создать таблицы, если они не существуют.""" 
        async with self.get_db_connection() as db: 
            await db.execute(''' CREATE TABLE IF NOT EXISTS carts ( 
                             cart_id INTEGER PRIMARY KEY, 
                             user_id INTEGER NOT NULL, 
                             status TEXT NOT NULL DEFAULT "active", 
                             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP) ''') 
            
            await db.execute(''' CREATE TABLE IF NOT EXISTS carts_items (
                              cart_item_id INTEGER PRIMARY KEY, 
                             cart_id INTEGER NOT NULL, 
                             product_id INTEGER NOT NULL, 
                             quantity INTEGER NOT NULL DEFAULT 1, 
                             license_id INTEGER NOT NULL, 
                             added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                             FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ) ''') 
            await db.commit()

class CartManager:
    """Менеджер для работы с корзинами."""

    def __init__(self, db: Database):
        self.db = db
    
    async def get_cart_by_user_id(self, user_id: int, status: str = 'active') -> Optional[Cart]:
        """Получить корзину по user_id и статусу."""
        result = await self.db.fetch_one(
            'SELECT * FROM carts WHERE user_id = ? AND status = ?', 
            (user_id, status)
        )
        return Cart(*result) if result else None

    async def create_cart(self, user_id: int, created_at: int) -> Cart:
        """Создать корзину для пользователя."""
        await self.db.execute(
            'INSERT INTO carts (user_id, created_at) VALUES (?, ?)', 
            (user_id, created_at)
        )
        return await self.get_cart_by_user_id(user_id, 'active')

    async def update_cart_status(self, cart: Cart, status: str, updated_at: int) -> None:
        """Обновить статус корзины."""
        cart.status = status
        cart.updated_at = updated_at
        await self.db.execute(
            'UPDATE carts SET status = ?, updated_at = ? WHERE cart_id = ?', 
            (status, updated_at, cart.cart_id)
        ) 
    

class CartItemManager:
    """Менеджер для работы с товарами в корзине."""

    def __init__(self, db: Database):
        self.db = db

    async def add_item_to_cart(self, cart: Cart, product_id: int, license_id: int, added_at: int, quantity: int = 1) -> None:
        """Добавить товар в корзину."""
        await self.db.execute(
            'INSERT INTO carts_items (cart_id, product_id, quantity, license_id, added_at) VALUES (?, ?, ?, ?, ?)', 
            (cart.cart_id, product_id, quantity, license_id, added_at)
        )

    async def remove_item_from_cart(self, cart: Cart, product_id: int) -> None:
        """Удалить товар из корзины."""
        await self.db.execute(
            'DELETE FROM carts_items WHERE cart_id = ? AND product_id = ?', 
            (cart.cart_id, product_id)
        )

    async def get_items_from_cart(self, cart: Cart) -> List[CartItem]:
        """Получить все товары из корзины."""
        rows = await self.db.fetch_all( 
            'SELECT cart_item_id, cart_id, product_id, quantity, license_id, added_at FROM carts_items WHERE cart_id = ?', 
            (cart.cart_id,)
        )
        return [CartItem(*row) for row in rows]

    async def clear_cart(self, cart: Cart) -> None:
        """Очистить корзину."""
        await self.db.execute(
            'DELETE FROM carts_items WHERE cart_id = ?', 
            (cart.cart_id,)
        )

    async def count_items_in_cart(self, cart: Cart) -> int: 
        """Посчитать количество товаров в корзине.""" 
        result = await self.db.fetch_one(
             'SELECT COUNT(*) FROM carts_items WHERE cart_id = ?', 
             (cart.cart_id,) ) 
        return result[0] if result else 0

    async  def check_item_in_cart(self, cart:Cart, product_id: int)-> CartItem:
        """Найти совпадение по product_id"""
        cart_item = await self.db.fetch_all(
            'SELECT * FROM carts_items WHERE product_id = ? AND cart_id = ?',
            (product_id,cart.cart_id,)
        )
        return cart_item if cart_item else None
class ShoppingCartService:
    """Сервис для работы с корзинами и товарами."""

    def __init__(self):
        self.db = Database()
        self.cart_manager = CartManager(self.db)
        self.cart_item_manager = CartItemManager(self.db)
        self._initialize_db() 
    def _initialize_db(self): 
        loop = asyncio.get_event_loop() 
        loop.run_until_complete(self.db.create_tables())
    async def get_or_create_cart(self, user_id: int, created_at: int) -> Cart:
        """Получить корзину или создать новую."""
        cart = await self.cart_manager.get_cart_by_user_id(user_id)
        return cart if cart else await self.cart_manager.create_cart(user_id, created_at)

    async def add_item(self, user_id: int, product_id: int, license_id: int, added_at: int, quantity: int = 1) -> None:
        """Добавить товар в корзину."""
        cart = await self.get_or_create_cart(user_id, added_at)
        await self.cart_item_manager.add_item_to_cart(cart, product_id, license_id, added_at, quantity)

    async def remove_item(self, user_id: int, product_id: int) -> None:
        """Удалить товар из корзины."""
        cart = await self.get_or_create_cart(user_id, 0)  # Неважно время, просто нужен cart_id
        await self.cart_item_manager.remove_item_from_cart(cart, product_id)

    async def get_cart_items(self, user_id: int) -> List[CartItem]:
        """Получить все товары в корзине пользователя."""
        cart = await self.get_or_create_cart(user_id, 0)
        return await self.cart_item_manager.get_items_from_cart(cart)

    async def clear_cart(self, user_id: int) -> None:
        """Очистить корзину пользователя."""
        cart = await self.get_or_create_cart(user_id, 0)
        await self.cart_item_manager.clear_cart(cart)

    async def update_status(self, user_id: int, status: str, updated_at: int) -> None:
        """Обновить статус корзины для пользователя."""
        cart = await self.get_or_create_cart(user_id, 0)  # Неважно время, просто нужен cart_id
        await self.cart_manager.update_cart_status(cart, status, updated_at)

    async def count_items_in_cart(self, user_id: int) -> int: 
        """Посчитать количество товаров в корзине пользователя.""" 
        cart = await self.get_or_create_cart(user_id, 0)
        return await self.cart_item_manager.count_items_in_cart(cart)
    
    async def check_item_in_cart(self,user_id:int,product_id: int) -> CartItem:
        """Найти совпадение по product_id у пользователя"""
        cart = await self.get_or_create_cart(user_id, 0)
        return await self.cart_item_manager.check_item_in_cart(cart,product_id)

