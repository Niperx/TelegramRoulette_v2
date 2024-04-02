import logging
import sqlite3
import asyncio
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
    text = f'{balance}'
    await message.answer(text, reply_markup=get_menu_kb())


@router.message(F.text == '📈 Leaders')
async def cmd_check_balance(message: types.Message):
    print(get_info_about_user_message(message))
    user_id = message.from_user.id

    lead_text = "⭐️ ТОП-10 богатейших людей этого чёртово казино! ⭐️️ \n\n"
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

    await message.answer(lead_text, reply_markup=get_menu_kb())


#
#
# @router.message(F.text == '📺 Видео инсрукция подключения')
# async def cmd_raffle_info(message: types.Message):
#     print(get_info_about_user_message(message))
#     text = 'https://youtu.be/SWxzCXslK8k'
#     await message.answer(text, reply_markup=get_menu_kb())
#
#
# @router.message(F.text == '🎁 Призы')
# async def cmd_raffle_info(message: types.Message):
#     print(get_info_about_user_message(message))
#     text = 'У нас 3 призовых места каждый день:\n' \
#            '🥇 1 место - приз 30$\n' \
#            '🥈 2 место - приз 20$\n' \
#            '🥉 3 место - приз 10$\n'
#     await message.answer(text, reply_markup=get_menu_kb())
#
#
# @router.message(Command(commands=["cancel"]))
# @router.message(F.text.lower() == "отмена")
# async def cmd_cancel(message: types.Message, state: FSMContext):
#     await state.clear()
#     await message.answer(
#         text="Действие отменено",
#         reply_markup=get_menu_kb()
#     )




# @router.message(F.text == '💵 ЖМИ Участвовать')
# async def cmd_reg(message: types.Message, state: FSMContext):
#     print(get_info_about_user_message(message))
#     x = await check_user_id(message.from_user.id)
#     if x:
#         await message.answer('Ты уже в списках, дружочек', reply_markup=get_menu_kb())
#     else:
#         # тут переход в другое состояние
#         # await create_user(message.from_user.id, '1111', message.from_user.username,
#         #                   f'https://t.me/id{message.from_user.id}')
#
#         await message.answer('Введите ваш UID на BingX (цифры)', reply_markup=get_cancel_kb())
#         await state.set_state(RegComp.giving_uid)


# @router.message(RegComp.giving_uid,
#                 F.text)
# async def cmd_give_uid(message: types.Message, state: FSMContext):
#     print(get_info_about_user_message(message))
#     try:
#         uid = int(message.text.lower())
#         chk = await check_uid(uid)
#         if chk:
#             await message.answer(
#                 text='Такой UID уже присутствует в базе, попробуйте ещё раз',
#                 reply_markup=get_cancel_kb())
#         else:
#             await state.update_data(uid=message.text.lower())
#             await message.answer(
#                 text='Включите копирование "DEPOSIT BOOSTER # 1" и пришлите СКРИНШОТ\n\n'
#                      'Видео инструкция как это сделать - https://youtu.be/SWxzCXslK8k',
#                 reply_markup=get_cancel_kb())
#             await state.set_state(RegComp.giving_photo)
#     except:
#         await message.answer('Неверный UID', reply_markup=get_menu_kb())
#         await state.clear()
#
#
# @router.message(RegComp.giving_photo,
#                 F.photo)
# async def cmd_give_photo(message: types.Message, state: FSMContext):
#     print(get_info_about_user_message(message))
#     await message.forward(503516164)
#     user_data = await state.get_data()
#     if message.from_user.username:
#         await bot.send_message(503516164,
#                                f'ID: #^{message.from_user.id}^#\n#*<a href="https://t.me/{message.from_user.username}">{message.from_user.username}</a>*#\nUID: ^^{user_data["uid"]}^^',
#                                parse_mode='HTML', reply_markup=get_aprove_kb())
#         await message.answer('Отправили на модерацию вашу заявку на участие, ожидайте...', reply_markup=get_menu_kb())
#
#     else:
#         await message.answer('Упс! У вас отсутствует никнейм в телеграме, укажите его в настройках профиля и попробуйте ещё раз')
#     await state.clear()
#
#
# @router.callback_query(F.data.startswith('aprove_'))
# async def callbacks_aprove(callback: types.CallbackQuery):
#     action = callback.data.split('_')[-1]
#     print(action)
#     text = callback.message.text
#     user_id = text[text.find('#^') + 2:text.find('^#')]
#     user_link = text[text.find('#*') + 2:text.find('*#')]
#     user_uid = text[text.find('^^') + 2:text.rfind('^^')]
#     if action == 'yes':
#         print(user_id, user_link, user_uid)
#         await create_user(user_id, user_uid, link=f'https://t.me/{user_link}')
#         num = await get_number(user_id)
#         await bot.send_message(int(user_id), f'Вы зарегистрированы на участие в конкурсе под номером {num}\n\n'
#                                              '▪️ Канал бота - https://t.me/+-pCJY2_O-Js3OTUy\n\n'
#                                              '▪️ Чат бота - https://t.me/+WndscOY7L9I5NDdi')
#     elif action == 'no':
#         await bot.send_message(int(user_id), 'Заявка отклонена')
#     text = f'ID: {user_id}\n' \
#            f'Username: @{user_link}\n' \
#            f'UID: {user_uid}'
#     await callback.message.edit_text(text, parse_mode='HTML')

