import asyncio
import time

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config
from database import db
from helpers import fmt_time, get_link, not_joined, parse_payload, shorten

STICKER_TIME = 1  # seconds to show "choosing a sticker" first (0 = skip)


async def _action_loop(client, chat_id):
    """First 'choosing a sticker', then 'sending a file' until cancelled."""
    try:
        if STICKER_TIME > 0:
            await client.send_chat_action(chat_id, ChatAction.CHOOSE_STICKER)
            await asyncio.sleep(STICKER_TIME)
        while True:
            await client.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
            await asyncio.sleep(4)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


async def _send(client, uid, text, kb=None, pic=None):
    if pic:
        try:
            return await client.send_photo(uid, pic, caption=text, reply_markup=kb)
        except Exception:
            pass
    return await client.send_message(uid, text, reply_markup=kb)


# ---------- shortener verification ----------
async def verify_gate(client, uid, payload):
    """Return True if a verification message was sent (user must verify first)."""
    if await db.is_admin(uid):
        return False
    if not await db.get_setting("short_on", False):
        return False
    if await db.is_verified(uid):
        return False

    domain = await db.get_setting("short_url")
    api = await db.get_setting("short_api")
    if not domain or not api:
        return False

    token = await db.create_token(uid, payload)
    deep = f"https://t.me/{client.bot_username}?start=verify_{token}"
    short = await shorten(domain, api, deep)
    if not short:  # shortener down -> do not block users
        await db.del_token(token)
        return False

    rows = [[B("Click to download your file", url=short)]]
    extra = []
    tutorial = await db.get_setting("tutorial")
    premium = await db.get_setting("premium")
    if tutorial:
        extra.append(B("How to Open", url=tutorial))
    if premium:
        extra.append(B("Premium", url=premium))
    if extra:
        rows.append(extra)

    pic = await db.get_setting("verify_pic") or config.VERIFY_PIC
    await _send(client, uid, config.VERIFY_MSG, M(rows), pic)
    return True


async def handle_verify(client, uid, token):
    doc = await db.get_token(token)
    if not doc or doc["user_id"] != uid:
        return await client.send_message(uid, config.EXPIRED_MSG)

    await db.del_token(token)  # single use
    elapsed = time.time() - doc["created"]
    retry = f"https://t.me/{client.bot_username}?start={doc['payload']}"
    retry_kb = M([[B("♻️ Try Again", url=retry)]])

    if elapsed > config.TOKEN_EXPIRE:
        return await client.send_message(uid, config.EXPIRED_MSG, reply_markup=retry_kb)

    min_time = int(await db.get_setting("min_time", config.MIN_VERIFY_TIME))
    if elapsed < min_time:
        return await client.send_message(uid, config.BYPASS_MSG, reply_markup=retry_kb)

    hours = int(await db.get_setting("verify_hours", config.VERIFY_HOURS))
    await db.set_verified(uid, time.time() + hours * 3600)
    await client.send_message(
        uid,
        config.VERIFIED_MSG.format(hours=hours),
        reply_markup=M([[B("📥 Get your file", url=retry)]]),
    )


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
            await asyncio.sleep(STICKER_TIME)
            text = config.START_MSG.format(first=first)
            kb = M([
                [B("🤖 About Me", callback_data="about"), B("Settings ⚙️", callback_data="settings")],
                [B("Close ✖️", callback_data="close")],
            ])
            effect = {"message_effect_id": config.START_EFFECT} if config.START_EFFECT else {}
            if config.START_PIC:
                return await client.send_photo(uid, config.START_PIC, caption=text, reply_markup=kb, **effect)
            return await client.send_message(uid, text, reply_markup=kb, **effect)

        payload = message.command[1]

        # coming back from the short link
        if payload.startswith("verify_"):
            return await handle_verify(client, uid, payload[7:])

        # force subscribe check (max 6 channels, normal + request mode)
        missing, total = await not_joined(client, uid)
        if missing:
            await asyncio.sleep(STICKER_TIME)
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

        # shortener verification
        if await verify_gate(client, uid, payload):
            return

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
