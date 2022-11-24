import asyncio
import logging
import motor.motor_asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.filters.role import RoleFilter, AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.role import RoleMiddleware
from tgbot.services.repository import Repo

logger = logging.getLogger(__name__)


def create_connection(db_name):
    client = motor.motor_asyncio.AsyncIOMotorClient()
    db = client[db_name]
    return db


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config = load_config("bot.ini")

    storage = MemoryStorage()
    db_connection = create_connection(config.db.db_name)

    bot = Bot(token=config.tg_bot.token, parse_mode="html")
    print(await bot.get_me())
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(DbMiddleware(db_connection))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_id, Repo(db_connection)))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    register_admin(dp)
    register_user(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped")
