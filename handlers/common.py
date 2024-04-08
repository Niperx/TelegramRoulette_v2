# coding=utf-8
import asyncio
import logging

import aiogram.types

from db.db_manage import *
from config import TOKEN
from datetime import datetime
from aiogram import Bot, types, Router, F
from aiogram.filters.command import Command
from aiogram.filters import CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link

from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter

bot = Bot(token=TOKEN)
router = Router()


async def get_logs(text, username='Anonim', name='Anonim'):
    with open("logs.txt", "r", encoding="utf-8") as read_logs:
        logs_text = read_logs.read()

    now = datetime.now()
    now = datetime.strftime(now, '%d.%m %H:%M:%S')

    logs_text += f'## {now} ## @{username} ({name}) {text}\n'

    with open("logs.txt", "w", encoding="utf-8") as write_logs:
        write_logs.write(logs_text)


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


@router.message(ChatTypeFilter(chat_type=["private"]), Command(commands=["start"]))
@router.message(CommandStart(deep_link=True))
async def cmd_start(message: types.Message, command: CommandObject):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    text = 'Добро пожаловать в это  🎰 <b>Чёртово Казино</b> 🎰'

    user_id = message.from_user.id
    chk = await check_user_id(user_id)
    if not chk:
        balance = 10000
        code = command.args
        if code is not None and code.isdigit() and code != message.from_user.id:
            chk_ref = await check_user_id(int(code))
            if not chk_ref:
                code = None
            else:
                code = int(code)
                balance += 40000
                if message.from_user.username is not None:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}'
                                                f' - @{message.from_user.username}')
                else:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}')
                await add_money(code, balance)
            text += f'\n<i>(Ваш бонус: {balance} коинов по реферальной системе)</i>'
        await create_user(user_id, message.from_user.username, balance, code)

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(Command(commands=["balance"]))
@router.message(F.text == '💰 Balance')
async def cmd_check_balance(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    user_id = message.from_user.id
    balance = await get_balance(user_id)
    text = (f'🪙 <b>Ваш баланс:</b> 🪙\n'
            f'{int(balance)}')
    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'проверил свой баланс на сумму {int(balance)} коинов', message.from_user.username, message.from_user.first_name)


@router.message(Command(commands=["leaders"]))
@router.message(F.text == '📈 Leaders')
async def cmd_check_leaders(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')

    lead_text = "⭐️ <b>ТОП-10 богатейших людей этого чёртово казино!</b> ⭐️️ \n\n"
    tops_db = await get_leaders(10)

    i = 0
    for top in tops_db:
        i += 1
        smile = ''
        if i <= 3:
            match i:
                case 1:
                    smile = '🥇 '
                case 2:
                    smile = '🥈 '
                case 3:
                    smile = '🥉 '
        else:
            smile = '🎗 '
        you_mark = ''
        if message.from_user.username == top[0]:
            you_mark = '(You)'

        lead_text += f'{smile} {i}. @{top[0]} - {int(top[1])} коинов. {smile} {you_mark}\n'

    await message.answer(lead_text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'посмотрел список лидеров', message.from_user.username, message.from_user.first_name)


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '💲 Daily')
async def cmd_get_daily(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    user_id = message.from_user.id

    time_left = await check_money_time(user_id)

    if time_left // 3600 <= 23:
        end = 3600 * 24 - time_left
        end_h = int(end // 3600)
        end_m = int(end % 3600 / 60)
        text = f'🪙 До бесплатных монеток осталось: 🪙 \n<b>{end_h}ч. {end_m}м.</b>'
        log_text = f'проверил оставшееся время до получения дневной нормы'
    else:
        money = 10000
        await add_money(user_id, money)
        await update_money_time(user_id)
        text = (f'🪙 Вам начислено 10000 монеток 🪙\n'
                f'Приходите за новой порцией через <b>24ч.</b>')
        log_text = f'получил дневную норму {money}'

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(log_text, message.from_user.username, message.from_user.first_name)


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '📊 Stats')
async def cmd_check_stats(message: types.Message):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    user_id = message.from_user.id
    link = await create_start_link(bot, f'{user_id}')
    text = f'<b>Ваша реферальная ссылка:</b> <i>(кликабельно)</i>\n <code>{link}</code>\n\n'

    stats = await get_stats()
    red, green, black = stats[0], stats[1], stats[2]

    text += (f'📊 <b>Статистика:</b> 📊\n\n'
             f'🟥 Красный цвет выпал {red} раз(а) 🟥 ({round(red / (red + green + black) * 100)}%)\n\n'
             f'🟩 Зелёный цвет выпал {green} раз(а) 🟩 ({round(green / (red + green + black) * 100)}%)\n\n'
             f'⬛️ Чёрный цвет выпал {black} раз(а) ⬛️ ({round(black / (red + green + black) * 100)}%)\n\n'
             f'Общее число бросков - {red + green + black} раз(а)')

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
    await get_logs(f'посмотрел статистику рандома', message.from_user.username, message.from_user.first_name)


@router.message(Command(commands=["clear"]))
async def cmd_check_stats(message: types.Message):
    a = await message.answer('Клавиатура удалена', reply_markup=aiogram.types.ReplyKeyboardRemove())
    await asyncio.sleep(1)
    await a.delete()
