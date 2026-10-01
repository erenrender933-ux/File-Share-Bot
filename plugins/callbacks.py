from pyrogram import Client
from pyrogram.types import InlineKeyboardButton as B, InlineKeyboardMarkup as M

import config
from database import db
from helpers import fmt_time

HOME_KB = M([
    [B("🤖 About Me", callback_data="about"), B("Settings ⚙️", callback_data="settings")],
    [B("Close ✖️", callback_data="close")],
])
BACK_KB = M([[B("⬅️ Back", callback_data="back"), B("Close ✖️", callback_data="close")]])


@Client.on_callback_query()
async def cb(client, q):
    if q.data == "close":
        await q.message.delete()
    elif q.data == "about":
        await _edit(q, config.ABOUT_MSG, BACK_KB)
    elif q.data == "back":
        await _edit(q, config.START_MSG.format(first=q.from_user.mention), HOME_KB)
    elif q.data == "settings":
        if not await db.is_admin(q.from_user.id):
            return await q.answer("Admins only.", show_alert=True)
        delay = int(await db.get_setting("auto_delete", config.AUTO_DELETE_TIME))
        text = (
            "⚙️ <b>CONFIGURATIONS</b>\n\n"
            f"◈ Total force sub channel: <code>{len(await db.get_fsubs())}</code>\n"
            f"◈ Total admins: <code>{len(await db.admin_list())}</code>\n"
            f"◈ Total banned users: <code>{len(await db.banned_list())}</code>\n"
            f"◈ Auto delete mode: <code>{'Enabled (' + fmt_time(delay) + ')' if delay else 'Disabled'}</code>"
        )
        await _edit(q, text, BACK_KB)
    await q.answer()


async def _edit(q, text, kb):
    if q.message.photo:
        await q.message.edit_caption(text, reply_markup=kb)
    else:
        await q.message.edit_text(text, reply_markup=kb)
