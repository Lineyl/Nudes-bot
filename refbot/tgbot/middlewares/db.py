from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from tgbot.services.repository import Repo


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection

    async def pre_process(self, obj, data, *args):
        db = self.db_connection
        data["db"] = db
        data["repo"] = Repo(db)

    async def post_process(self, obj, data, *args):
        del data["repo"]

