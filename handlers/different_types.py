import logging
from aiogram import Router, F
from aiogram.types import Message
from datetime import datetime, date

router = Router()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_info_about_user_message(message):  # Инфа о сообщении в консоль
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {message.from_user.id}, Text: {message.text}, Chat ID: {message.chat.id}'
    try:
        text += f'\nUsername: {message.from_user.username},' \
                f' Name: {message.from_user.first_name},' \
                f' Surname: {message.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


def get_info_about_user_callback(callback):  # Инфа о коллбеке в консоль
    text = f'\n##### {datetime.now()} #####\n'
    text += f'ID: {callback.from_user.id}, Text: {callback.data}'
    try:
        text += f'\nUsername: {callback.from_user.username},' \
                f' Name: {callback.from_user.first_name},' \
                f' Surname: {callback.from_user.last_name} '
    except Exception as e:
        logging.exception(e)
        text += 'Нет имени'
    return text


@router.message(F.photo)
async def message_with_text(message: Message):
    print(get_info_about_user_message(message))
    await message.answer("Это фото!")

# @router.message(F.sticker)
# async def message_with_sticker(message: Message):
#     await message.answer("Это стикер!")
#
# @router.message(F.animation)
# async def message_with_gif(message: Message):
#     await message.answer("Это GIF!")