import asyncio
from src.methods.database.carts_manager import ShoppingCartService
from src.methods.database.licenses_manager import LicensesDatabase
from src.methods.database.licenses_products_manager import LicensesProductsDatabase
from src.methods.database.orders_manager import OrdersService
from src.methods.database.products_manager import ProductsDatabase
from src.methods.database.users_manager import UsersDatabase
from src.methods.database.wishlists_manager import WishlistsDatabase

async def init_databases() -> None:
    shopping_cart_service = ShoppingCartService()
    await shopping_cart_service._initialize_db() 
    await LicensesDatabase.create_table()
    await LicensesProductsDatabase.create_table()
    order_service = OrdersService()
    await order_service.create_table()
    await ProductsDatabase.create_table()
    await UsersDatabase.create_table()
    await WishlistsDatabase.create_table()

# # Пример вызова
# if __name__ == '__main__':
#     asyncio.run(init_databases())
