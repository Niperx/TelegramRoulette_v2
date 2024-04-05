import logging
import config
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import common, play
from db.db_manage import check_db

bot = Bot(token=config.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
main_router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # await check_db()  # Проверка на существование ДБ

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    dp.include_routers(
        common.router,
        play.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
