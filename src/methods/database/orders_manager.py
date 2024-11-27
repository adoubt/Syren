import aiosqlite
from typing import Any, List, Optional, Tuple
from loguru import logger

# Настройка логирования
logger.add("src/logs/orders.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip")
logger.add("src/logs/errors.log", format="{time} {level} {message}", level="ERROR", rotation="5 MB", compression="zip")

class OrdersDAL:
    DB_PATH = "src/databases/orders.db"
    
    # SQL Queries
    CREATE_TABLE_QUERY = '''CREATE TABLE IF NOT EXISTS orders(
                                order_id INTEGER PRIMARY KEY,
                                user_id INTEGER NOT NULL,
                                promo_code_id INTEGER DEFAULT NULL,
                                status TEXT CHECK(status IN ('pending', 'paid', 'expired', 'failed')) DEFAULT 'pending',
                                total_amount REAL NOT NULL DEFAULT 0.0,
                                payment_method TEXT,
                                currency TEXT NOT NULL DEFAULT 'USD',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                paid_at TIMESTAMP DEFAULT NULL)'''

    INSERT_ORDER_QUERY = '''INSERT INTO orders(user_id, promo_code_id, total_amount, payment_method, cart_id)
                            VALUES (?, ?, ?, ?, ?)'''

    SELECT_ORDER_VALUE_QUERY = '''SELECT {key} FROM orders WHERE order_id = ?'''
    SELECT_ORDERS_BY_STATUS_QUERY = '''SELECT * FROM orders WHERE status = ?'''
    SELECT_ORDERS_BY_USER_QUERY = '''SELECT * FROM orders WHERE user_id = ?{status_clause}'''
    UPDATE_ORDER_VALUE_QUERY = '''UPDATE orders SET {key} = ? WHERE order_id = ?'''
    DELETE_ORDERS_BY_USER_AND_STATUS_QUERY = '''DELETE FROM orders WHERE user_id = ? AND status = ?'''
    SELECT_ORDER_ID_BY_USER_AND_STATUS_QUERY = '''SELECT order_id FROM orders WHERE user_id = ? AND status = ?'''

    @classmethod
    async def create_table(cls) -> None:
        logger.info("Creating orders table if not exists")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            await db.execute(cls.CREATE_TABLE_QUERY)
            await db.commit()

    @classmethod
    async def create_order(cls, user_id: int, cart_id: int, total_amount: float, payment_method: str = 'crypto',
                           promo_code_id: Optional[int] = None) -> int:
        logger.info(f"Creating order for user_id {user_id} with cart_id {cart_id}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            try:
                cursor = await db.execute(cls.INSERT_ORDER_QUERY,
                                          (user_id, promo_code_id, total_amount, payment_method, cart_id))
                await db.commit()
                order_id = cursor.lastrowid
                logger.info(f"Order created with id {order_id}")
                return order_id
            except Exception as e:
                logger.error(f"Error creating order for user_id {user_id}: {e}")
                raise

    @classmethod
    async def get_order_value(cls, order_id: int, key: str) -> Optional[Any]:
        query = cls.SELECT_ORDER_VALUE_QUERY.format(key=key)
        logger.info(f"Getting {key} value for order_id {order_id}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            cursor = await db.execute(query, (order_id,))
            result = await cursor.fetchone()
            if result:
                logger.info(f"Found {key} for order_id {order_id}")
                return result[0]
            else:
                logger.info(f"No {key} found for order_id {order_id}")
                return None
    
    @classmethod
    async def get_orders_by_status(cls, status: str) -> List[Tuple]:
        logger.info(f"Getting orders with status {status}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            cursor = await db.execute(cls.SELECT_ORDERS_BY_STATUS_QUERY, (status,))
            return await cursor.fetchall()
    
    @classmethod
    async def get_orders_by_user(cls, user_id: int, status: Optional[str] = None) -> List[Tuple]:
        status_clause = ' AND status = ?' if status else ''
        params = [user_id, status] if status else [user_id]
        query = cls.SELECT_ORDERS_BY_USER_QUERY.format(status_clause=status_clause)
        logger.info(f"Getting orders for user_id {user_id} with status {status}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            cursor = await db.execute(query, params)
            return await cursor.fetchall()

    @classmethod
    async def update_order_value(cls, order_id: int, key: str, value: Any) -> None:
        query = cls.UPDATE_ORDER_VALUE_QUERY.format(key=key)
        logger.info(f"Updating {key} value for order_id {order_id}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            await db.execute(query, (value, order_id))
            await db.commit()

    @classmethod
    async def delete_orders_by_user_and_status(cls, user_id: int, status: str) -> None:
        logger.info(f"Deleting orders for user_id {user_id} with status {status}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            await db.execute(cls.DELETE_ORDERS_BY_USER_AND_STATUS_QUERY, (user_id, status))
            await db.commit()

    @classmethod
    async def get_order_id_by_user_and_status(cls, user_id: int, status: str) -> Optional[int]:
        logger.info(f"Getting order_id for user_id {user_id} with status {status}")
        async with aiosqlite.connect(cls.DB_PATH) as db:
            cursor = await db.execute(cls.SELECT_ORDER_ID_BY_USER_AND_STATUS_QUERY,
                                      (user_id, status))
            result = await cursor.fetchone()
            return result[0] if result else None


class OrdersService:
    def __init__(self):
        self.orders_dal = OrdersDAL()

    async def create_order(self, user_id: int, cart_id: int, total_amount: float, payment_method: str = 'crypto',
                           promo_code_id: Optional[int] = None) -> int:
        return await self.orders_dal.create_order(user_id, cart_id, total_amount, payment_method, promo_code_id)

    async def get_order_status(self, order_id: int) -> Optional[str]:
        return await self.orders_dal.get_order_value(order_id, 'status')

    async def get_pending_orders(self) -> List[Any]:
        return await self.orders_dal.get_orders_by_status('pending')

    async def get_user_orders(self, user_id: int, status: Optional[str] = None) -> List[Any]:
        return await self.orders_dal.get_orders_by_user(user_id, status)

    async def update_order_status(self, order_id: int, status: str, paid_at: Optional[int] = None) -> None:
        await self.orders_dal.update_order_value(order_id, 'status', status)
        if paid_at:
            await self.orders_dal.update_order_value(order_id, 'paid_at', paid_at)

    async def delete_pending_orders(self, user_id: int) -> None:
        await self.orders_dal.delete_orders_by_user_and_status(user_id, 'pending')

    async def get_pending_order_id(self, user_id: int) -> Optional[int]:
        return await self.orders_dal.get_order_id_by_user_and_status(user_id, 'pending')
