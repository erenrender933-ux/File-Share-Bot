import asyncio
import base64
import logging
import config
import json
import aiohttp
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M
from database import db

log = logging.getLogger(__name__)


# ---------- link encoding ----------
def encode(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def decode(text: str) -> str:
    text += "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text.encode()).decode()


def make_link(client, first_id, last_id=None):
    k = abs(config.DB_CHANNEL)
    raw = f"get-{first_id * k}" if last_id is None else f"get-{first_id * k}-{last_id * k}"
    return f"https://t.me/{client.bot_username}?start={encode(raw)}"


def parse_payload(payload):
    """Return list of DB-channel message ids, or None if invalid."""
    try:
        parts = decode(payload).split("-")
        k = abs(config.DB_CHANNEL)
        if parts[0] != "get":
            return None
        if len(parts) == 2:
            return [int(parts[1]) // k]
        if len(parts) == 3:
            a, b = int(parts[1]) // k, int(parts[2]) // k
            return list(range(a, b + 1)) if a <= b else list(range(a, b - 1, -1))
    except Exception:
        return None
    return None


def fmt_time(seconds: int) -> str:
    if seconds % 3600 == 0:
        h = seconds // 3600
        return f"{h} Hour{'s' if h > 1 else ''}"
    if seconds % 60 == 0:
        m = seconds // 60
        return f"{m} Minute{'s' if m > 1 else ''}"
    return f"{seconds} Seconds"


# ---------- force subscribe ----------
async def _is_joined(client, ch, user_id):
    cid = ch["_id"]
    try:
        m = await client.get_chat_member(cid, user_id)
        if m.status in (ChatMemberStatus.BANNED, ChatMemberStatus.LEFT):
            raise UserNotParticipant()
        if m.status == ChatMemberStatus.RESTRICTED and not getattr(m, "is_member", True):
            raise UserNotParticipant()
        return True
    except UserNotParticipant:
        if ch["mode"] == "request" and await db.has_request(cid, user_id):
            return True
        return False
    except Exception as e:
        log.warning("fsub check failed for %s: %s (is the bot admin there?)", cid, e)
        return True  # don't block users because of a broken channel


async def not_joined(client, user_id):
    channels = await db.get_fsubs()
    missing = [ch for ch in channels if not await _is_joined(client, ch, user_id)]
    return missing, len(channels)


async def get_link(client, ch):
    if ch.get("link"):
        return ch["link"]
    try:
        inv = await client.create_chat_invite_link(ch["_id"], creates_join_request=(ch["mode"] == "request"))
        await db.set_fsub_link(ch["_id"], inv.invite_link)
        return inv.invite_link
    except Exception as e:
        log.error("could not create invite link for %s: %s", ch["_id"], e)
        return None


# ---------- auto delete worker ----------
async def autodelete_worker(client):
    while True:
        try:
            for doc in await db.due_deletes():
                try:
                    await client.delete_messages(doc["chat_id"], doc["ids"])
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    continue  # retry next loop
                except Exception:
                    pass
                await db.remove_delete(doc["_id"])

                payload = doc.get("payload")
                if payload:
                    try:
                        kb = M([[
                            B("♻️ Click Here", url=f"https://t.me/{client.bot_username}?start={payload}"),
                            B("Close ✖️", callback_data="close"),
                        ]])
                        await client.send_message(doc["chat_id"], config.DELETED_MSG, reply_markup=kb)
                    except Exception as e:
                        log.warning("could not send deleted notice: %s", e)
        except Exception as e:
            log.error("autodelete worker: %s", e)
        await asyncio.sleep(15)
