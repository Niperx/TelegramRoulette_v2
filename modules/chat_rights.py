from aiogram.filters import Filter
from aiogram import types
from modules.admins_list import ADMINS

# moderator_groups = {
#     'aprove': -1001710827731,
# }


class IsAdmin(Filter):
    key = 'is_admin'

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: types.Message):
        if message.from_user.is_bot == True or message.from_user.first_name == 'Group' or message.from_user.id in ADMINS:
            return True


class IsPrivate(Filter):
    key = 'is_private'

    def __init__(self, is_private):
        self.is_private = is_private

    async def check(self, message: types.Message):
        if message.chat.type == 'private':
            return True


# class IsReplyToBot(Filter):
#     key = 'is_reply_to_bot'
#
#     def __init__(self, is_reply_to_bot):
#         self.is_reply_to_bot = is_reply_to_bot
#
#     async def check(self, message: types.Message):
#         if message.reply_to_message:
#             if message.reply_to_message.from_user.is_bot and message.reply_to_message.from_user.id == 6088769515 and message.chat.id == moderator_groups['aprove']:
#                 return True