from pyrogram import Client, filters

from database import db


async def _is_admin(_, __, m):
    return bool(m.from_user) and await db.is_admin(m.from_user.id)


admin = filters.create(_is_admin)


def _mask(key):
    return key[:4] + "****" if key else "Not set"


@Client.on_message(filters.command("shortener") & filters.private & admin)
async def shortener(client, m):
    if len(m.command) > 1:
        arg = m.command[1].lower()
        if arg == "on":
            if not await db.get_setting("short_url") or not await db.get_setting("short_api"):
                return await m.reply("❌ Set <code>/setshorturl</code> and <code>/setshortapi</code> first.")
            await db.set_setting("short_on", True)
            return await m.reply("✅ Shortener <b>ON</b>.")
        if arg == "off":
            await db.set_setting("short_on", False)
            return await m.reply("✅ Shortener <b>OFF</b>.")
        return await m.reply("Usage: <code>/shortener on</code> or <code>/shortener off</code>")

    on = await db.get_setting("short_on", False)
    await m.reply(
        "🔗 <b>SHORTENER SETTINGS</b>\n\n"
        f"◈ Status: <code>{'ON' if on else 'OFF'}</code>\n"
        f"◈ Short URL: <code>{await db.get_setting('short_url') or 'Not set'}</code>\n"
        f"◈ API: <code>{_mask(await db.get_setting('short_api'))}</code>\n"
        f"◈ Tutorial: <code>{await db.get_setting('tutorial') or 'Not set'}</code>\n"
        f"◈ Premium: <code>{await db.get_setting('premium') or 'Not set'}</code>\n"
        f"◈ Verify pic: <code>{'Set' if await db.get_setting('verify_pic') else 'Not set'}</code>\n"
        f"◈ Verified hours: <code>{await db.get_setting('verify_hours', 12)}</code>\n"
        f"◈ Bypass min seconds: <code>{await db.get_setting('min_time', 60)}</code>"
    )


@Client.on_message(filters.command("setshorturl") & filters.private & admin)
async def setshorturl(client, m):
    if len(m.command) < 2:
        return await m.reply("Usage: <code>/setshorturl gplinks.in</code>")
    domain = m.command[1].replace("https://", "").replace("http://", "").strip("/")
    await db.set_setting("short_url", domain)
    await m.reply(f"✅ Short URL set: <code>{domain}</code>\nNow send <code>/setshortapi YOUR_API_KEY</code>")


@Client.on_message(filters.command("setshortapi") & filters.private & admin)
async def setshortapi(client, m):
    if len(m.command) < 2:
        return await m.reply("Usage: <code>/setshortapi YOUR_API_KEY</code>")
    await db.set_setting("short_api", m.command[1])
    try:
        await m.delete()  # hide the key from the chat
    except Exception:
        pass
    await client.send_message(
        m.chat.id, "✅ API saved (message deleted for safety).\nNow send <code>/shortener on</code>"
    )


@Client.on_message(filters.command("settutorial") & filters.private & admin)
async def settutorial(client, m):
    if len(m.command) < 2 or not m.command[1].startswith("http"):
        return await m.reply("Usage: <code>/settutorial https://t.me/yourchannel/12</code>")
    await db.set_setting("tutorial", m.command[1])
    await m.reply("✅ How to Open link saved.")


@Client.on_message(filters.command("setpremium") & filters.private & admin)
async def setpremium(client, m):
    if len(m.command) < 2 or not m.command[1].startswith("http"):
        return await m.reply("Usage: <code>/setpremium https://t.me/youradmin</code>")
    await db.set_setting("premium", m.command[1])
    await m.reply("✅ Premium link saved.")


@Client.on_message(filters.command("setverifypic") & filters.private & admin)
async def setverifypic(client, m):
    r = m.reply_to_message
    arg = m.command[1] if len(m.command) > 1 else ""
    if arg.lower() == "remove":
        await db.set_setting("verify_pic", "")
        return await m.reply("✅ Verify picture removed.")
    if r and r.photo:
        pic = r.photo.file_id
    elif arg.startswith("http"):
        pic = arg
    else:
        return await m.reply(
            "Usage:\nReply to a photo with <code>/setverifypic</code>\n"
            "or <code>/setverifypic https://link/to/image.jpg</code>\n"
            "or <code>/setverifypic remove</code>"
        )
    await db.set_setting("verify_pic", pic)
    await m.reply("✅ Verify picture saved.")


@Client.on_message(filters.command("setverifytime") & filters.private & admin)
async def setverifytime(client, m):
    if len(m.command) < 2 or not m.command[1].isdigit() or int(m.command[1]) < 1:
        return await m.reply("Usage: <code>/setverifytime 12</code> (hours, minimum 1)")
    await db.set_setting("verify_hours", int(m.command[1]))
    await m.reply("✅ Verified time updated.")


@Client.on_message(filters.command("setmintime") & filters.private & admin)
async def setmintime(client, m):
    if len(m.command) < 2 or not m.command[1].isdigit():
        return await m.reply("Usage: <code>/setmintime 60</code> (seconds)")
    await db.set_setting("min_time", int(m.command[1]))
    await m.reply("✅ Bypass minimum time updated.")
