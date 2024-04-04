import logging
from db.db_manage import *
from config import TOKEN
from datetime import datetime
from aiogram import Bot, types, Router, F
from aiogram.filters.command import Command

from modules.buttons_list import *

bot = Bot(token=TOKEN)
router = Router()


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


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    print(get_info_about_user_message(message))
    user_id = message.from_user.id
    balance = 10000
    chk = await check_user_id(user_id)
    if not chk:
        code = message.text
        code = code[code.find(' ') + 1:]
        print(f'ЭТО КОД РЕФЕРАЛА {code}')
        if code.isdigit() and code != message.from_user.id:
            chk_ref = await check_user_id(int(code))
            if not chk_ref:
                code = None
            else:
                code = int(code)
                balance += 50000
                if message.from_user.username is not None:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}'
                                                f' - @{message.from_user.username})')
                else:
                    await bot.send_message(chat_id=code,
                                           text=f'У вас новый реферал {message.from_user.first_name}')
        else:
            code = None
        await create_user(user_id, message.from_user.username, balance, code)

    text = 'Добро пожаловать в это  🎰 <b>Чёртово Казино</b> 🎰'
    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(F.text == '💰 Balance')
async def cmd_check_balance(message: types.Message):
    print(get_info_about_user_message(message))
    user_id = message.from_user.id
    balance = await get_balance(user_id)
    text = (f'<b>Ваш баланс:</b>\n'
            f'🪙 {balance} 🪙')
    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(F.text == '📈 Leaders')
async def cmd_check_balance(message: types.Message):
    print(get_info_about_user_message(message))

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

        lead_text += f'{smile} {i}. @{top[0]} - {top[1]} коинов. {smile} {you_mark}\n'

    await message.answer(lead_text, reply_markup=get_menu_kb(), parse_mode='HTML')


@router.message(F.text == '💲 Daily')
async def cmd_check_balance(message: types.Message):
    print(get_info_about_user_message(message))
    user_id = message.from_user.id

    time_left = await check_money_time(user_id)
    print(f'Часы: {24 - time_left // 3600}, Минуты: {60 - time_left % 3600}')
    print(time_left // 3600)
    if time_left // 3600 <= 23:
        end = 3600 * 24 - time_left
        end_h = int(end // 3600)
        end_m = int(end % 3600 / 60)
        text = f'🪙 До бесплатных монеток осталось: 🪙 \n<b>{end_h}ч. {end_m}м.</b>'
    else:
        await add_money(user_id, 10000)
        await update_money_time(user_id)
        text = (f'🪙 Вам начислено 10000 монеток 🪙\n'
                f'Приходите за новой порцией через <b>24ч.</b>')

    await message.answer(text, reply_markup=get_menu_kb(), parse_mode='HTML')
