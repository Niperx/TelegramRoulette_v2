import logging
from db.db_manage import *
from config import TOKEN
from datetime import datetime
from aiogram import Bot, types, Router, F
from aiogram.filters import or_f
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from modules.buttons_list import *

bot = Bot(token=TOKEN)
router = Router()


class RegComp(StatesGroup):
    betting = State()


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


@router.message(F.text == '🟥 Red')
@router.message(F.text == '🟩 Green')
@router.message(F.text == '⬛️ Black')
async def cmd_check_balance(message: types.Message, state: FSMContext):
    print(get_info_about_user_message(message))
    await state.update_data(color=message.text)
    data = await state.get_data()
    try:  # Сделать проверку, без try
        last = data['last']
    except:
        last = 1000
        await state.update_data(last=last)

    await message.answer(f'Ставка на Цвет: {message.text}\n'
                         f'<i>(Сумма в центре клавиатуры)</i>', reply_markup=get_bet_kb(last), parse_mode='HTML')


@router.callback_query(F.data.startswith('bet_'))
async def process_edit_bet(callback: types.CallbackQuery, state: FSMContext):
    print(get_info_about_user_callback(callback))
    print(callback.data)
    balance = await get_balance(callback.from_user.id)
    data = await state.get_data()
    last_raw = data['last']
    last = data['last']
    match callback.data:
        case 'bet_min_10': last -= 10
        case 'bet_min_100': last -= 100
        case 'bet_plus_10': last += 10
        case 'bet_plus_100': last += 100
        case 'bet_div': last /= 2
        case 'bet_double': last *= 2
        case 'bet_standard': last = balance / 10
        case 'bet_allin': last = balance

    if last <= 0:
        last = 10
    elif last > balance:
        last = balance

    last = int(last)
    await state.update_data(last=last)
    await callback.message.edit_text(f'Ставка на Цвет: {data['color']}\n'
                                     f'<i>(Сумма в центре клавиатуры)</i>', reply_markup=get_bet_kb(last), parse_mode='HTML')
