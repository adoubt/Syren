from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def get_choose_licenses_kb(user_id,product_id,licenses,disabled) -> InlineKeyboardMarkup:
    buttons = []
    for license in licenses:
         if license[0] not in disabled:
            # buttons = buttons+[InlineKeyboardButton(text=f'{license[2]} | {license[4]} USD', callback_data=f"addToCart_{product_id}_{license[0]}_{user_id}")]
            buttons = buttons+[InlineKeyboardButton(text=f'{license[2]} | {license[4]} USD', callback_data=f"addToCart_{product_id}_{license[0]}_{user_id}")]
    
    back = []
    back.append(InlineKeyboardButton(text='Back', callback_data=f"showcase_{product_id}")) 
    rows= [[btn] for btn in buttons] + [back]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
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
    back.append(InlineKeyboardButton(text='Back', callback_data=f"beat_{product_id}")) 
    rows= [[btn] for btn in buttons] + [back]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb   

def get_licenses_kb(licenses)-> InlineKeyboardMarkup:
    
    buttons = []
    for license in licenses: 
        is_archived,feature = license[9], license[5]
        meta_preview = ''
        if is_archived == 1:
            meta_preview += '🗃'
        if feature ==1:
            meta_preview += '⭐️'
        buttons = buttons+[InlineKeyboardButton(text=f'{meta_preview}{license[2]}', callback_data=f"license_{license[0]}")]
    footer = []
    footer.append(InlineKeyboardButton(text='➕ New License', callback_data=f"newlicense")) 
    footer.append(InlineKeyboardButton(text='♻️ To Default', callback_data=f"setdefaultlicenses"))
    rows= [[btn] for btn in buttons] + [footer]
    ikb = InlineKeyboardMarkup(inline_keyboard=rows)
    return ikb

def get_showcase_kb(product_id:int, is_sold:int, channel:str, already_in_wishlist:int,price:int| None = None) -> InlineKeyboardMarkup:
    # if already_in_cart ==1:
    #     cart_btn = [InlineKeyboardButton(text=f'Go To Cart', callback_data='cart')]
    # else:
    cart_btn = [InlineKeyboardButton(text=f'From {price} USD', callback_data=f'choose_license_{product_id}')]
    if already_in_wishlist ==1:
        wishlist_btn = [InlineKeyboardButton(text=f'Go To wishlist', callback_data='cart')]
    else:
        wishlist_btn = [InlineKeyboardButton(text=f'➕ Add to Wishlist', callback_data=f'choose_license_{product_id}')]



    channel_btn = [InlineKeyboardButton(text=f'Channel', url=channel)]

    if is_sold == 0:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
        cart_btn,
        wishlist_btn,
        channel_btn,
        ]) 
    else:
        ikb = InlineKeyboardMarkup(inline_keyboard=[
        wishlist_btn,
        channel_btn,
    ]) 
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
#         [InlineKeyboardButton(text=f"Pay {price} USD", callback_data=f'Pay_{user_id}_{product_id}')],
#         [InlineKeyboardButton(text="Remove❌", callback_data=f'delItemFromCart_{user_id}_{product_id}')],
#     ]) 
#     return ikb
# def get_total_in_cart_kb()
def get_item_in_wishlist_kb(user_id,product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buy 🛒", callback_data=f'showcase_{product_id}')],
        [InlineKeyboardButton(text="Remove ❌", callback_data=f'delItemFromWishlist_{user_id}_{product_id}')],
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
    # pagination.append(InlineKeyboardButton(text='⏪', callback_data=f"getprompts_first_{current_page}"))
    # if current_page > 1:
    pagination.append(InlineKeyboardButton(text='◀️', callback_data=f"mybeats_{current_page-1}"))
    pagination.append(InlineKeyboardButton(text = f"{current_page+1}/{total_pages}", callback_data="current_page"))
    # if current_page < total_pages:
    pagination.append(InlineKeyboardButton(text='▶️', callback_data=f"mybeats_{current_page+1}"))
    # if current_page!= total_pages:
    # pagination.append(InlineKeyboardButton(text='⏩', callback_data=f"getprompts_last_{current_page}"))

    # buttons.append(pagination)
    
    # footer.append(InlineKeyboardButton(text='Удалить все', callback_data="del_products"))
    # back = []
    # back.append(InlineKeyboardButton(text='Back', callback_data="homepage"))
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
        [InlineKeyboardButton(text="Delete Beat", callback_data=f'delproduct_0_{product_id}')], 
        
        [InlineKeyboardButton(text="Back", callback_data=f'mybeats_0')],
    ]) 
    return ikb
def get_editbeatname_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data=f'beat_{product_id}')],
    ]) 
    return ikb
    
def get_delbeat_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Delete", callback_data=f'delproduct_1_{product_id}'),
        InlineKeyboardButton(text="Back", callback_data=f'beat_{product_id}')],
    ]) 
    return ikb

def get_files_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Mp3", callback_data=f'showfile_mp3_{product_id}'),
         InlineKeyboardButton(text=f"Edit", callback_data=f'editfile_mp3_{product_id}')],
        [InlineKeyboardButton(text=f"Wav", callback_data=f'showfile_wav_{product_id}'),
         InlineKeyboardButton(text=f"Edit", callback_data=f'editfile_wav_{product_id}')],
        [InlineKeyboardButton(text=f"Stems", callback_data=f'showfile_stems_{product_id}'),
         InlineKeyboardButton(text=f"Edit", callback_data=f'editfile_stems_{product_id}')],
        [InlineKeyboardButton(text=f"Preview", callback_data=f'showfile_preview_{product_id}'),
         InlineKeyboardButton(text=f"Edit", callback_data=f'editfile_preview_{product_id}')],
        [InlineKeyboardButton(text=f"Back", callback_data=f'beat_{product_id}')]
    ]) 
    return ikb

def get_editfile_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Back", callback_data=f'files_{product_id}')]
    ]) 
    return ikb

def get_hide_file_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Hide", callback_data=f'hide_file')]
    ]) 
    return ikb

def get_edit_file_back_kb(product_id)-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Back", callback_data=f'files_{product_id}')]
    ]) 
    return ikb

def get_newbeat_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Skip", callback_data=f'skip_stems')],
        [InlineKeyboardButton(text=f"Cancel", callback_data=f'cancel')]
    ]) 
    return ikb

def get_cancel_kb()-> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Cancel", callback_data=f'cancel')]
    ]) 
    return ikb

def get_main_buyer_kb(cart) -> ReplyKeyboardMarkup:
    cart_view = 'Cart'
    if cart > 0:cart_view = f'Cart({cart})'
    rkb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🏠 Home',callback_data='homepage'),
         
        KeyboardButton(text='⚙️ Settings', callback_data='settings')],
        [KeyboardButton(text='🤍 Wishlist')],
        
        [KeyboardButton(text='🌏 Sell Beats', callback_data='seller')]],resize_keyboard=True
    )
    return rkb

def get_main_seller_kb() -> ReplyKeyboardMarkup:
    
    rkb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='🏠 Home',callback_data='homepage'),
        KeyboardButton(text='➕ New Beat')],
        [KeyboardButton(text='📼 My Beats', callback_data='mybeats_0'),
        KeyboardButton(text='📂 My Licenses')],
        [KeyboardButton(text='⚙️ Settings', callback_data='settings_1'),
         KeyboardButton(text='🌏 Buy Beats', callback_data='buyer')]],resize_keyboard=True
    )
    return rkb

def get_cart_buyer_kb(total) -> ReplyKeyboardMarkup:
    
    rkb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=f' Pay ${total}')],
        [KeyboardButton(text='Back')]],resize_keyboard=True
    )
    return rkb