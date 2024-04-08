import asyncio
import logging
import random

from db.db_manage import *
from config import TOKEN
from datetime import datetime
from aiogram import Bot, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from modules.buttons_list import *
from modules.chat_type import ChatTypeFilter

bot = Bot(token=TOKEN)
router = Router()


class RegComp(StatesGroup):
    betting = State()


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


@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '🟥 Red')
@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '🟩 Green')
@router.message(ChatTypeFilter(chat_type=["private"]), F.text == '⬛️ Black')
async def cmd_choose_color(message: types.Message, state: FSMContext):
    print(await get_info_about_user_message(message))
    await bot.send_chat_action(chat_id=message.chat.id, action='typing')
    balance = await get_balance(message.from_user.id)
    await state.update_data(color=message.text)
    data = await state.get_data()
    print(data)
    if 'message' in data.keys():
        if data['message'] is not None:
            a = data['message']
            await a.delete()

    if 'last' in data.keys():
        last = data['last']
    else:
        last = 1000
        await state.update_data(last=last)

    if last <= balance:
        last = int(balance) / 10
        await state.update_data(last=last)

    if balance > 0:
        a = await message.answer(f'Ставка на Цвет: {message.text}\n'
                                 f'<i>(Сумма в центре клавиатуры, либо напишите её сообщением)</i>',
                                 reply_markup=get_bet_kb(last), parse_mode='HTML')
        await state.update_data(message=a)
    else:
        await message.answer(f'У вас недостаточно средств на балансе 😢',
                             reply_markup=get_menu_kb(), parse_mode='HTML')


@router.callback_query(F.data == 'bet_no')
async def process_cancel_bet(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    await callback.message.edit_text('❌ <b>Ставка отменена</b> ❌', parse_mode='HTML')
    await state.update_data(color=None)


@router.callback_query(F.data == 'bet_yes')
async def process_confirm_bet(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    await bot.send_chat_action(chat_id=callback.message.chat.id, action='typing')

    balance = await get_balance(callback.from_user.id)
    username = await get_username(callback.from_user.id)
    data = await state.get_data()
    last = data['last']
    color = data['color']

    await callback.message.edit_text(callback.message.text)

    roll = random.randint(0, 14)
    roll_pic_raw = "✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️✖️\n⬛️🟥⬛️🟥⬛️🟥🟩🟥⬛️🟥⬛️🟥⬛️🟥⬛️\n"

    roll_start = "🎰 Крутим рулетку 🎰\n\n"
    roll_pic = roll_pic_raw[:roll * 2] + '🎲' + roll_pic_raw[roll * 2 + 1:]
    text = roll_start + roll_pic_raw

    a = await callback.message.answer(text)
    await asyncio.sleep(0.5)
    text = roll_start + roll_pic
    await a.edit_text(text)

    bet_color = None
    if roll == 6:
        # green
        bet_color = '🟩 Green 🟩'
        await change_stats('green')
    elif roll % 2 == 0:
        # black
        bet_color = '⬛️ Black ⬛️'
        await change_stats('black')
    elif roll % 2 == 1:
        # red
        bet_color = '🟥 Red 🟥'
        await change_stats('red')

    text += f"\nНа барабане следующий цвет:\n{bet_color}️\n\n@{username}, "

    await asyncio.sleep(1)

    if color:
        if color in bet_color:
            if 'Green' in bet_color:
                x = 13
            else:
                x = 2
            text += f'Вы выиграли {last * x - last} коинов'
            log_text = f'Выиграл {last * x - last} коинов'

            await add_money(callback.from_user.id, last * x - last)
            await a.edit_text(text)
            await state.update_data(message=None)
        else:
            text += f'Вы проиграли {last} коинов'
            log_text = f'Проиграл {last} коинов'

            await add_money(callback.from_user.id, -last)
            await a.edit_text(text)
            await state.update_data(message=None)

        await get_logs(f'Сделал ставку на {color}. Выпало {bet_color}. {log_text}', callback.from_user.username, callback.from_user.first_name)
    else:
        await a.edit_text('❌ <b>Ставка отменена</b> ❌ \n(Защита от спама)', parse_mode='HTML')

    await state.update_data(color=None)


@router.callback_query(F.data == 'bet_now')
async def process_cancel_bet(callback: types.CallbackQuery):
    print(await get_info_about_user_callback(callback))


@router.callback_query(F.data.startswith('bet_'))
async def process_edit_bet(callback: types.CallbackQuery, state: FSMContext):
    print(await get_info_about_user_callback(callback))
    print(callback.data)
    await bot.send_chat_action(chat_id=callback.message.chat.id, action='typing')

    balance = await get_balance(callback.from_user.id)
    data = await state.get_data()
    last = data['last']
    start_last = last
    match callback.data:
        case 'bet_min_10':
            last -= 10
        case 'bet_min_100':
            last -= 100
        case 'bet_plus_10':
            last += 10
        case 'bet_plus_100':
            last += 100
        case 'bet_div':
            last /= 2
        case 'bet_double':
            last *= 2
        case 'bet_standard':
            last = balance / 10
        case 'bet_allin':
            last = balance

    if last <= 0:
        last = 10
    elif last > balance:
        last = balance

    last = int(last)

    if start_last != last:
        await state.update_data(last=last)
        text = f'Ставка на Цвет: {data["color"]}\n<i>(Сумма в центре клавиатуры, либо напишите её сообщением)</i>'
        a = await callback.message.edit_text(text, reply_markup=get_bet_kb(last), parse_mode='HTML')
        await state.update_data(message=a)


# @router.message(ChatTypeFilter(chat_type=["private"]), F.text)
# async def cmd_choose_color(message: types.Message, state: FSMContext):
#     print(await get_info_about_user_message(message))
#     await bot.send_chat_action(chat_id=message.chat.id, action='typing')
#
#     balance = await get_balance(message.from_user.id)
#     data = await state.get_data()
#
#     if 'color' in data.keys():
#         if data['color'] is not None:
#             if message.text.isdigit():
#                 bet = int(message.text)
#                 if bet <= balance:
#                     await state.update_data(last=bet)
#                     my_message = data['message']
#                     text = (f'Ставка на Цвет: {data["color"]}\n<i>(Сумма в центре клавиатуры, либо напишите её '
#                             f'сообщением)</i>')
#                     await my_message.edit_text(text, reply_markup=get_bet_kb(bet), parse_mode='HTML')
#
#     await message.delete()
