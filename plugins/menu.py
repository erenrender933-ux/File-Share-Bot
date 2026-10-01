import os
import sys

from pyrogram import Client, filters

import config


def _make(name):
    @Client.on_message(filters.command(name) & filters.private)
    async def _h(client, m):
        await m.reply(config.HELP_TEXTS[name])
    _h.__name__ = f"{name}_cmd"
    return _h


for _n in ("help", "users", "forcesub", "req_fsub", "files", "auto_del", "cmd"):
    _make(_n)


@Client.on_message(filters.command("restart") & filters.private & filters.user(config.OWNER_ID))
async def restart_cmd(client, m):
    await m.reply("♻️ <b>Restarting...</b>")
    os.execl(sys.executable, sys.executable, *sys.argv)
