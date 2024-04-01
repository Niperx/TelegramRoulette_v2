from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# def get_menu_kb():
#

def get_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text='🟥 Red'),
        KeyboardButton(text='⬛️ Green'),
        KeyboardButton(text='🟩 Black')
    )
    builder.row(
        KeyboardButton(text='💲 Daily'),
        KeyboardButton(text='💰 Balance')
    )

    builder.row(
        KeyboardButton(text='📊 Stats'),
        KeyboardButton(text='📈 Leaders')
    )

    return builder.as_markup(resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Отмена')
    kb.adjust(1)

    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Что делаем?")


