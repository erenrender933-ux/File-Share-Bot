import asyncio
import logging
import sys

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.types import BotCommand

import config
from database import db
from helpers import autodelete_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("bot")


class Bot(Client):
    def __init__(self):
        super().__init__(
            "fileshare-bot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=50,
            in_memory=True,
            parse_mode=ParseMode.HTML,
        )
        self.bot_username = ""
        self._task = None

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.bot_username = me.username
        await db.setup()
        try:
            test = await self.send_message(config.DB_CHANNEL, "✅ DB channel check")
            await test.delete()
        except Exception as e:
            log.error("Cannot post in DB_CHANNEL %s: %s (add the bot as admin there)", config.DB_CHANNEL, e)
            sys.exit(1)
        await self.set_bot_commands([BotCommand(c, d) for c, d in config.BOT_COMMANDS])
        self._task = asyncio.create_task(autodelete_worker(self))
        log.info("Bot started as @%s", self.bot_username)

    async def stop(self, *args):
        if self._task:
            self._task.cancel()
        await super().stop()
        log.info("Bot stopped")


if __name__ == "__main__":
    Bot().run()
