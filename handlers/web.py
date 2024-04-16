# coding=utf-8
import asyncio
import logging
import os.path
import aiogram.types

from aiogram import Bot, types, Router, F
from aiogram.filters.command import Command
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link

from db.db_manage import *
from config import TOKEN

from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter

bot = Bot(token=TOKEN)
router = Router()


async def get_info_about_user_message(message):  # Инфа о сообщении в консоль
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


async def get_info_about_user_callback(callback):  # Инфа о коллбеке в консоль
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


@router.message(Command(commands=["web"]))
async def cmd_web(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    await message.reply('Click!', reply_markup=get_webapp_kb())


