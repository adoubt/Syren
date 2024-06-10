from pytonconnect import TonConnect

from src.misc import MANIFEST_URL
from tc_storage import TcStorage


def get_connector(chat_id: int):
    return TonConnect(MANIFEST_URL, storage=TcStorage(chat_id))