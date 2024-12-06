from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from src.misc import LINK
from typing import Any
def get_choose_licenses_kb(
    user_id, product_id, licenses, disabled, feature: int = None, in_cart: int = None
) -> InlineKeyboardMarkup:
    buttons = []

    # Логика определения выбранной лицензии (selected_license)
    # Если в корзине есть товар, то он считается выбранным. Если нет, берем рекомендованную.

    for license in licenses:
        license_id=license[0]
        if license_id not in disabled:
            # Формируем текст кнопки с ценой
            price = license[4]
            price = int(price) if price.is_integer() else price
            text = f"{license[2]} ${price}"
            callback_data = f"addToCart:product_id={product_id}&license_id={license_id}&user_id={user_id}"
            if license_id == in_cart:
                text = f'🛒 View in Cart ›'
                callback_data = "cart"
            # Добавляем звезду для рекомендованной лицензии
            if license_id == feature and license_id != in_cart:
                text += " 🔹"
            
            # Меняем текст для активной выбранной лицензии
            
            
            # Добавляем кнопку в список
            buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Создаем footer с кнопками для навигации
    footer = [
        InlineKeyboardButton(text="‹ Back", callback_data=f"showcase_{product_id}")
    ]

    # Возвращаем разметку с кнопками
    inline_keyboard = buttons + [footer]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_generated_cart_kb(cart_items, user_id, total_amount,payment_method) -> InlineKeyboardMarkup:

    # Генерация кнопок для товаров
    ikb = [
        [
            InlineKeyboardButton(text=item.get("name", "unknown item"), callback_data=f"showcase_{item.get('product_id', 'unknown')}"),
            InlineKeyboardButton(text="🗑️", callback_data=f"delFromCart_{item.get('product_id', 'unknown')}_{item.get('license_id', 'unknown')}_{user_id}_cart")
        ]
        for item in cart_items
    ]

    # Кнопки действий
    ikb += [
        #[InlineKeyboardButton(text="🗑️ Remove All", callback_data=f"clear_cart_{user_id}")],
        [InlineKeyboardButton(text=f"Method: {payment_method}", callback_data="choosePaymentMethod")],
        [InlineKeyboardButton(text=f"💳 Checkout ${total_amount}", callback_data=f"checkout")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=ikb)

def get_payment_methods_kb(default_payment_method:str,payment_methods: list):
    ikb = [
        [InlineKeyboardButton(text=f'• {method} •' if method == default_payment_method else method,callback_data=f'setDefaultPaymentMethod_{method}')

        ]
        for method in payment_methods
    ]
    ikb+= [ 
        [InlineKeyboardButton(text=f"‹ Back", callback_data="cart")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)
def get_order_summary_kb(amount)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Pay {amount}', pay=True)],
        [InlineKeyboardButton(text="cancel",callback_data="paystarscancel")]
        ]) 
    return ikb

def get_paystars_kb(amount)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Pay {amount}⭐️', pay=True)],
        [InlineKeyboardButton(text="cancel",callback_data="paystarscancel")]
        ]) 
    return ikb
def get_product_licenses_kb(product_id:int,licenses,disabled)-> InlineKeyboardMarkup:
    
    buttons = []
    for license in licenses:
        for item in disabled:
            if license[0] == item[0]:
                buttons = buttons+[InlineKeyboardButton(text=f'[ ] {license[2]}', callback_data=f"enable_{product_id}_{license[0]}")]
                break
        else:
            buttons = buttons+[InlineKeyboardButton(text=f'[✔️] {license[2]}', callback_data=f"disable_{product_id}_{license[0]}")]
    back = []
    back.append(InlineKeyboardButton(text='‹ Back', callback_data=f"beat_{product_id}")) 
    rows= [[btn] for btn in buttons] + [back]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb   

def get_licenses_kb(licenses)-> InlineKeyboardMarkup:
    
    buttons = []
    for license in licenses: 
        is_archived,feature, is_active = license[10], license[5], license[12]
        meta_preview = ''
        if is_archived == 1:
            meta_preview += '🗃'
        if feature ==1:
            meta_preview += '🔹'
        if is_active !=1:
            meta_preview +='💤'
        buttons = buttons+[InlineKeyboardButton(text=f'{meta_preview}{license[2]}', callback_data=f"mylicense_{license[0]}")]
    footer = []
    footer.append(InlineKeyboardButton(text='➕ New License', callback_data=f"newlicense")) 
    footer.append(InlineKeyboardButton(text='♻️ To Default', callback_data=f"setdefaultlicenses"))
    rows= [[btn] for btn in buttons] + [footer]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_mylicense_kb(license) -> InlineKeyboardMarkup:
    license_id = license[0]
    feature, is_active, price,  license_type = license[5], license[12], license[4], license[6]

    name_btn = InlineKeyboardButton(text="Name", callback_data=f"licenseedit_name_{license_id}")
    desc_btn = InlineKeyboardButton(text="Description", callback_data=f"licenseedit_desc_{license_id}")

    license_texts = {
        0: "Edit license type",
        1: "MP3",
        2: "MP3, WAV",
    }
    type_text = 'Include: '+license_texts.get(license_type, "MP3, WAV, STEMS")
    type_btn = InlineKeyboardButton(text=type_text, callback_data=f"licenseedit_type_{license_id}")

    active_text = "Activate" if is_active != 1 else "💤 Deactivate"
    active_btn = InlineKeyboardButton(text=active_text, callback_data=f"licenseedit_active_{license_id}_{1 if is_active != 1 else 0}")
    price = int(price) if price.is_integer() else price
    price_text = "Edit price" if price is None else '$'+str(price)
    price_btn = InlineKeyboardButton(text=price_text, callback_data=f"licenseedit_price_{license_id}")

    feature_text = "Set as featured🔹" if feature != 1 else "Unset as featured"
    feature_btn = InlineKeyboardButton(text=feature_text, callback_data=f"licenseedit_feature_{license_id}_{1 if feature != 1 else 0}")

    contract_btns = [
        InlineKeyboardButton(text="Contract", callback_data=f"licenseedit_showfile_{license_id}"),
        InlineKeyboardButton(text="Edit", callback_data=f"licenseedit_uploadfile_{license_id}")
    ]

    delete_btn = InlineKeyboardButton(text="🗑", callback_data=f"licenseedit_delete_{license_id}")
    back_btn = InlineKeyboardButton(text="‹ Back", callback_data="mylicenses")

    rows = [
        [active_btn],
        [name_btn, desc_btn],
        [type_btn],
        [price_btn],
        [feature_btn],
        [btn for btn in contract_btns if btn is not None],
        [delete_btn],
        [back_btn],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_showcase_kb(product_id:int, is_sold:int, channel:str, already_in_wishlist:int,already_in_cart:int,user_id: int,price:float| None = None) -> InlineKeyboardMarkup:
    buttons = []
    if already_in_cart ==1:
        cart_btn = [InlineKeyboardButton(text=f'In 🛒 Cart', callback_data=f'chooseLicense:product_id={product_id}')]
        
    else:
        cart_btn = [InlineKeyboardButton(text=f'${price}', callback_data=f'chooseLicense:product_id={product_id}')]
    if not is_sold or not price:
        buttons.append(cart_btn)    
    if already_in_wishlist ==1:
        wishlist_btn = [InlineKeyboardButton(text=f'In 🤍 Wishlist', callback_data=f'delFromWishlist_{user_id}_{product_id}_refresh')]
    else:
        wishlist_btn = [InlineKeyboardButton(text=f'🤍', callback_data=f'addTowishlist_{product_id}')]
    buttons.append(wishlist_btn)
    if channel: 
        channel_btn = [InlineKeyboardButton(text=f'Channel', url=channel)]
        buttons.append(channel_btn)
    # if is_sold == 1 or not price:
    #     ikb = InlineKeyboardMarkup(inline_keyboard=[
    #     wishlist_btn,
    #     channel_btn,
    #     ]) 
        
    # else:
    #     ikb = InlineKeyboardMarkup(inline_keyboard=[
    #     cart_btn,
    #     wishlist_btn,
    #     channel_btn,
    # ]) 
    ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return ikb

def get_homepage_kb(user_id, cart)-> InlineKeyboardMarkup:
    cart_view = 'Cart'
    if cart > 0:cart_view = f'Cart({cart})'
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cart_view, callback_data='cart')],
        [InlineKeyboardButton(text='My Beats', callback_data='mybeats_0')],
        [InlineKeyboardButton(text='Settings', callback_data='settings')]
    ]) 
    return ikb

def get_settings_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        # [InlineKeyboardButton(text="Change Language", callback_data='change_languge')],
        [InlineKeyboardButton(text="Notification", callback_data='notifications')],
        
    ]) 
    return ikb

# def get_item_in_cart_kb(user_id,product_id,license_name,price,description, license_file)-> InlineKeyboardMarkup:
#     ikb = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=f"Pay {price} ⭐", callback_data=f'Pay_{user_id}_{product_id}')],
#         [InlineKeyboardButton(text="Remove❌", callback_data=f'delItemFromCart_{user_id}_{product_id}')],
#     ]) 
#     return ikb
# def get_total_in_cart_kb()
def get_item_in_wishlist_kb(user_id,product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Shop", callback_data=f'showcase_{product_id}'),
        InlineKeyboardButton(text="🗑", callback_data=f'delFromWishlist_{user_id}_{product_id}_del')],
    ]) 
    return ikb

def get_my_beats_kb(products,current_page:int, total_pages:int)-> InlineKeyboardMarkup:
    # header = []
    
    # header.append(InlineKeyboardButton(text='➕ New Beat', callback_data="new_beat"))
    buttons = []
    for product in products:
        name = product[2]
        product_id = product[0]
        buttons = buttons+[InlineKeyboardButton(text=name, callback_data=f"beat_{product_id}")]
    pagination = []
    # if current_page != 1:
    # pagination.append(InlineKeyboardButton(text='<<', callback_data=f"getprompts_first_{current_page}"))
    # if current_page > 1:
    pagination.append(InlineKeyboardButton(text='<', callback_data=f"mybeats_{current_page-1}"))
    pagination.append(InlineKeyboardButton(text = f"{current_page+1}/{total_pages}", callback_data="current_page"))
    # if current_page < total_pages:
    pagination.append(InlineKeyboardButton(text='>', callback_data=f"mybeats_{current_page+1}"))
    # if current_page!= total_pages:
    # pagination.append(InlineKeyboardButton(text='>>', callback_data=f"getprompts_last_{current_page}"))

    # buttons.append(pagination)
    
    # footer.append(InlineKeyboardButton(text='Удалить все', callback_data="del_products"))
    # back = []
    # back.append(InlineKeyboardButton(text='‹ Back', callback_data="homepage"))
    # buttons.append(footer)
    if total_pages>1:
        rows=  [[btn] for btn in buttons] + [pagination] 
    else: rows=  [[btn] for btn in buttons] 
    
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb


def get_beat_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Edit Name", callback_data=f'editproductname_{product_id}')],
        [InlineKeyboardButton(text="Files", callback_data=f'files_0_{product_id}'),
        InlineKeyboardButton(text=f"Licenses", callback_data=f'licenses_{product_id}')],
        [InlineKeyboardButton(text="🗑", callback_data=f'delproduct_0_{product_id}')], 
        
        [InlineKeyboardButton(text="‹ Back", callback_data=f'mybeats_0')],
    ]) 
    return ikb
def get_editbeatname_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="‹ Back", callback_data=f'beat_{product_id}')],
    ]) 
    return ikb
    
def get_delbeat_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑", callback_data=f'delproduct_1_{product_id}'),
        InlineKeyboardButton(text="‹ Back", callback_data=f'beat_{product_id}')],
    ]) 
    return ikb

def get_files_kb(product_id, preview_link, mp3_link, wav_link, stems_link) -> InlineKeyboardMarkup:
    buttons = []

    def add_buttons(file_type, link):
        if link:
            buttons.append(
                [
                    InlineKeyboardButton(text=file_type, callback_data=f'showfile_{file_type}_{product_id}'),
                    InlineKeyboardButton(text="Edit", callback_data=f'editfile_{file_type}_{product_id}')
                ]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(text=f"Upload {file_type}", callback_data=f'editfile_{file_type}_{product_id}')]
            )

    add_buttons("mp3", mp3_link)
    add_buttons("wav", wav_link)
    add_buttons("stems", stems_link)
    add_buttons("preview", preview_link)
    
    buttons.append(
        [InlineKeyboardButton(text="‹ Back", callback_data=f'beat_{product_id}')]
    )

    # Преобразуем список кнопок в InlineKeyboardMarkup
    return InlineKeyboardMarkup(inline_keyboard=buttons)




def get_editfile_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"‹ Back", callback_data=f'files_{product_id}')]
    ]) 
    return ikb

def get_hide_file_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Hide", callback_data=f'hide_file')]
    ]) 
    return ikb

def get_edit_file_kb(product_id,file_type)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"‹ Back", callback_data=f'files_{product_id}')],
        [InlineKeyboardButton(text=f"🗑", callback_data=f'deletefile_{file_type}_{product_id}')]
    ]) 
    return ikb

def get_newbeat_kb(reffer:str=None,params:Any=None)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Skip ›", callback_data=f'skip_stems')],
        [InlineKeyboardButton(text=f"Cancel", callback_data=f'cancel:reffer={reffer}&params={params}')]
    ]) 
    return ikb

def get_cancel_kb(reffer:str=None,params:Any=None)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Cancel", callback_data=f'cancel:reffer={reffer}&params={params}')]
    ]) 
    return ikb

def get_main_buyer_kb(wishlist_count: int, cart_count: int) -> ReplyKeyboardMarkup:

    cart_view = f'🛒 Cart({cart_count})' if cart_count > 0 else '🛒 Cart'
    wishlist_view = f'🤍 Wishlist({wishlist_count})' if wishlist_count > 0 else '🤍 Wishlist'

    rkb = ReplyKeyboardMarkup( 
        keyboard=[ 
            #[KeyboardButton(text='🏠 Home', callback_data='homepage'),
              [KeyboardButton(text='🛍 Purchases', callback_data='purchases'),
               KeyboardButton(text=cart_view, callback_data='cart')], 
              [KeyboardButton(text=wishlist_view),
               KeyboardButton(text=f'🤝 Offers')], 
               [KeyboardButton(text='⚙️ Settings', callback_data='settings'),
                KeyboardButton(text='🌏 Sell Beats', callback_data='seller')] 
                ],
                 resize_keyboard=True ) 
    return rkb

def get_main_seller_kb() -> ReplyKeyboardMarkup:
    
    rkb = ReplyKeyboardMarkup(keyboard=[
        #[KeyboardButton(text='🏠 Home',callback_data='homepage'),
        [KeyboardButton(text='➕ New Beat')],
        [KeyboardButton(text='📼 My Beats', callback_data='mybeats_0'),
        KeyboardButton(text='📂 My Licenses')],
        [KeyboardButton(text='⚙️ Settings', callback_data='settings_1'),
         KeyboardButton(text='🌏 Buy Beats', callback_data='buyer')]],resize_keyboard=True
    )
    return rkb

def get_link_kb(product_id:int,name:str=None)-> InlineKeyboardMarkup:
    text = name if name else 'link'
    url = LINK + str(product_id)
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, url=url)]
    ]) 
    return ikb