import urllib.parse

from aiogram.types import Message

def get_file_id(message: Message, file_type: str) -> str:
    # Проверка основного сообщения
    if message.audio and file_type in ['mp3', 'preview']:
        return message.audio.file_id
    elif message.document and file_type in ['wav', 'stems']:
        return message.document.file_id
    # Проверка вложенного сообщения
    elif message.reply_to_message:
        if message.reply_to_message.audio and file_type in ['mp3', 'preview']:
            return message.reply_to_message.audio.file_id
        elif message.reply_to_message.document and file_type in ['wav', 'stems']:
            return message.reply_to_message.document.file_id
    return None

def parse_callback_data(data: str) -> dict:
    # Удаляем префикс и парсим параметры
    query_string = data.split(':', 1)[1]
    return dict(urllib.parse.parse_qsl(query_string))
