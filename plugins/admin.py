import asyncio
import re

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config
from database import db
from helpers import fmt_time, make_link


async def _is_admin(_, __, m):
    return bool(m.from_user) and await db.is_admin(m.from_user.id)


admin = filters.create(_is_admin)
LINK_RE = re.compile(r"t\.me/c/\d+/(\d+)")


def share_kb(link):
    return M([[B("🔁 Share URL", url=f"https://t.me/share/url?url={link}")]])


# ---------- link generation ----------
MEDIA = filters.document | filters.video | filters.audio | filters.photo | filters.voice | filters.animation


@Client.on_message(filters.private & admin & MEDIA)
async def upload(client, m):
    """Admin sends a file -> stored in DB channel -> link returned."""
    stored = await m.copy(config.DB_CHANNEL)
    link = make_link(client, stored.id)
    await m.reply(f"<b>Here is your link:</b>\n\n{link}", quote=True, reply_markup=share_kb(link))


@Client.on_message(filters.command("genlink") & filters.private & admin)
async def genlink(client, m):
    if len(m.command) < 2 or not LINK_RE.search(m.command[1]):
        return await m.reply("Usage: <code>/genlink https://t.me/c/123456/45</code> (link of a post in the DB channel)")
    mid = int(LINK_RE.search(m.command[1]).group(1))
    link = make_link(client, mid)
    await m.reply(f"<b>Here is your link:</b>\n\n{link}", reply_markup=share_kb(link))


@Client.on_message(filters.command("batch") & filters.private & admin)
async def batch(client, m):
    found = [int(x) for x in LINK_RE.findall(" ".join(m.command[1:]))]
    if len(found) != 2:
        return await m.reply(
            "Usage: <code>/batch first_post_link last_post_link</code>\n"
            "Both links must be posts from the DB channel."
        )
    link = make_link(client, found[0], found[1])
    await m.reply(f"<b>Here is your batch link:</b>\n\n{link}", reply_markup=share_kb(link))


# ---------- stats / settings ----------
@Client.on_message(filters.command("stats") & filters.private & admin)
async def stats(client, m):
    await m.reply(f"👥 <b>Total users:</b> <code>{await db.count_users()}</code>")


@Client.on_message(filters.command("settings") & filters.private & admin)
async def settings(client, m):
    delay = int(await db.get_setting("auto_delete", config.AUTO_DELETE_TIME))
    protect = await db.get_setting("protect", config.PROTECT_CONTENT)
    await m.reply(
        "⚙️ <b>CONFIGURATIONS</b>\n\n"
        f"◈ Total force sub channels: <code>{len(await db.get_fsubs())}/{config.MAX_FSUB}</code>\n"
        f"◈ Total admins: <code>{len(await db.admin_list())}</code>\n"
        f"◈ Total banned users: <code>{len(await db.banned_list())}</code>\n"
        f"◈ Auto delete mode: <code>{'Enabled (' + fmt_time(delay) + ')' if delay else 'Disabled'}</code>\n"
        f"◈ Protect content: <code>{'On' if protect else 'Off'}</code>"
    )


@Client.on_message(filters.command("setdelete") & filters.private & admin)
async def setdelete(client, m):
    if len(m.command) < 2 or not m.command[1].isdigit():
        return await m.reply("Usage: <code>/setdelete 600</code> (seconds, 0 = off)")
    await db.set_setting("auto_delete", int(m.command[1]))
    await m.reply("✅ Auto delete updated.")


@Client.on_message(filters.command("setprotect") & filters.private & admin)
async def setprotect(client, m):
    if len(m.command) < 2 or m.command[1].lower() not in ("on", "off"):
        return await m.reply("Usage: <code>/setprotect on</code> or <code>off</code>")
    await db.set_setting("protect", m.command[1].lower() == "on")
    await m.reply("✅ Protect content updated.")


# ---------- force sub management (max 6) ----------
@Client.on_message(filters.command("addfsub") & filters.private & admin)
async def addfsub(client, m):
    if len(m.command) < 2 or not m.command[1].lstrip("-").isdigit():
        return await m.reply(
            "Usage:\n<code>/addfsub -1001234567890</code> (normal)\n"
            "<code>/addfsub -1001234567890 request</code> (join request)"
        )
    cid = int(m.command[1])
    mode = "request" if len(m.command) > 2 and m.command[2].lower().startswith("req") else "normal"
    existing = await db.get_fsubs()
    if len(existing) >= config.MAX_FSUB and not any(c["_id"] == cid for c in existing):
        return await m.reply(f"❌ Maximum {config.MAX_FSUB} force-sub channels reached.")
    try:
        chat = await client.get_chat(cid)
        me = await client.get_chat_member(cid, "me")
        if me.status != ChatMemberStatus.ADMINISTRATOR:
            return await m.reply("❌ Make the bot an admin (with invite-users permission) in that channel first.")
    except Exception as e:
        return await m.reply(f"❌ Cannot access that chat: <code>{e}</code>")
    await db.add_fsub(cid, chat.title, mode)
    await m.reply(f"✅ Added <b>{chat.title}</b> ({mode} mode).")


@Client.on_message(filters.command("delfsub") & filters.private & admin)
async def delfsub(client, m):
    if len(m.command) < 2 or not m.command[1].lstrip("-").isdigit():
        return await m.reply("Usage: <code>/delfsub -1001234567890</code>")
    await db.del_fsub(int(m.command[1]))
    await m.reply("✅ Removed.")


@Client.on_message(filters.command("fsubmode") & filters.private & admin)
async def fsubmode(client, m):
    if len(m.command) < 3 or not m.command[1].lstrip("-").isdigit() or m.command[2] not in ("normal", "request"):
        return await m.reply("Usage: <code>/fsubmode -1001234567890 request</code> or <code>normal</code>")
    await db.set_fsub_mode(int(m.command[1]), m.command[2])
    await m.reply("✅ Mode updated.")


@Client.on_message(filters.command("fsubs") & filters.private & admin)
async def fsubs(client, m):
    chs = await db.get_fsubs()
    if not chs:
        return await m.reply("No force-sub channels set.")
    await m.reply("\n".join(f"{i}. <b>{c['title']}</b> — <code>{c['_id']}</code> [{c['mode']}]" for i, c in enumerate(chs, 1)))


# ---------- admins & bans ----------
def _target(m):
    if len(m.command) > 1 and m.command[1].lstrip("-").isdigit():
        return int(m.command[1])
    if m.reply_to_message and m.reply_to_message.from_user:
        return m.reply_to_message.from_user.id


@Client.on_message(filters.command("addadmin") & filters.private & filters.user(config.OWNER_ID))
async def addadmin(client, m):
    uid = _target(m)
    if not uid:
        return await m.reply("Usage: <code>/addadmin user_id</code>")
    await db.add_admin(uid)
    await m.reply("✅ Admin added.")


@Client.on_message(filters.command("deladmin") & filters.private & filters.user(config.OWNER_ID))
async def deladmin(client, m):
    uid = _target(m)
    if not uid:
        return await m.reply("Usage: <code>/deladmin user_id</code>")
    await db.del_admin(uid)
    await m.reply("✅ Admin removed.")


@Client.on_message(filters.command("admins") & filters.private & admin)
async def admins(client, m):
    await m.reply("\n".join(f"• <code>{a}</code>" for a in await db.admin_list()))


@Client.on_message(filters.command("ban") & filters.private & admin)
async def ban(client, m):
    uid = _target(m)
    if not uid:
        return await m.reply("Usage: <code>/ban user_id</code>")
    await db.ban(uid)
    await m.reply("🚫 User banned.")


@Client.on_message(filters.command("unban") & filters.private & admin)
async def unban(client, m):
    uid = _target(m)
    if not uid:
        return await m.reply("Usage: <code>/unban user_id</code>")
    await db.unban(uid)
    await m.reply("✅ User unbanned.")


@Client.on_message(filters.command("banned") & filters.private & admin)
async def banned(client, m):
    ids = await db.banned_list()
    await m.reply("\n".join(f"• <code>{i}</code>" for i in ids) if ids else "No banned users.")


# ---------- broadcast ----------
@Client.on_message(filters.command("broadcast") & filters.private & admin)
async def broadcast(client, m):
    if not m.reply_to_message:
        return await m.reply("Reply to a message with /broadcast")
    users = await db.all_users()
    status = await m.reply(f"📣 Broadcasting to {len(users)} users...")
    ok = fail = 0
    for uid in users:
        try:
            await m.reply_to_message.copy(uid)
            ok += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await m.reply_to_message.copy(uid)
                ok += 1
            except Exception:
                fail += 1
        except Exception:
            fail += 1
            await db.del_user(uid)  # blocked / deleted account
        await asyncio.sleep(0.05)
    await status.edit(f"✅ <b>Broadcast done</b>\n\nSent: <code>{ok}</code>\nFailed/removed: <code>{fail}</code>")
