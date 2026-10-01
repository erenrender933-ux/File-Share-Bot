import asyncio
import time

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config
from database import db
from helpers import fmt_time, get_link, not_joined, parse_payload

# Status shown under the bot name. Other options: ChatAction.UPLOAD_DOCUMENT, ChatAction.TYPING
START_ACTION = ChatAction.CHOOSE_STICKER


async def _action_loop(client, chat_id):
    """Keep the chat status alive (Telegram clears it after ~5 seconds)."""
    try:
        while True:
            await client.send_chat_action(chat_id, START_ACTION)
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    uid = message.from_user.id
    first = message.from_user.mention

    if await db.is_banned(uid):
        return await message.reply("🚫 <b>You are banned from using this bot.</b>")
    await db.add_user(uid)

    # remove the /start command message from the chat
    try:
        await message.delete()
    except Exception:
        pass

    action_task = asyncio.create_task(_action_loop(client, uid))
    try:
        # plain /start
        if len(message.command) < 2:
            text = config.START_MSG.format(first=first)
            kb = M([
                [B("🤖 About Me", callback_data="about"), B("Settings ⚙️", callback_data="settings")],
                [B("Close ✖️", callback_data="close")],
            ])
            if config.START_PIC:
                return await client.send_photo(uid, config.START_PIC, caption=text, reply_markup=kb)
            return await client.send_message(uid, text, reply_markup=kb)

        payload = message.command[1]

        # force subscribe check (max 6 channels, normal + request mode)
        missing, total = await not_joined(client, uid)
        if missing:
            rows = []
            for ch in missing:
                link = await get_link(client, ch)
                if link:
                    rows.append([B(ch["title"], url=link)])
            rows.append([B("♻️ Try Again", url=f"https://t.me/{client.bot_username}?start={payload}")])
            return await client.send_message(
                uid,
                config.FORCE_MSG.format(first=first, missing=len(missing), total=total),
                reply_markup=M(rows),
            )

        ids = parse_payload(payload)
        if not ids:
            return await client.send_message(uid, "❌ <b>Invalid or expired link.</b>")

        protect = await db.get_setting("protect", config.PROTECT_CONTENT)
        sent = []

        for i in range(0, len(ids), 100):
            try:
                msgs = await client.get_messages(config.DB_CHANNEL, ids[i : i + 100])
            except Exception:
                continue
            for m in msgs:
                if not m or m.empty:
                    continue
                for attempt in range(2):
                    try:
                        copied = await m.copy(uid, protect_content=protect)
                        sent.append(copied)
                        break
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except Exception:
                        break

        if not sent:
            return await client.send_message(uid, "❌ <b>File not found. It may have been removed.</b>")

        delay = int(await db.get_setting("auto_delete", config.AUTO_DELETE_TIME))
        if delay > 0:
            note = await client.send_message(uid, config.DELETE_MSG.format(time=fmt_time(delay)))
            all_ids = [m.id for m in sent] + [note.id]
            await db.add_delete(uid, all_ids, time.time() + delay, payload)
    finally:
        action_task.cancel()
