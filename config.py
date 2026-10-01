import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "fileshare")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "0"))

OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x.lstrip("-").isdigit()]

MAX_FSUB = 6  # maximum force-sub channels
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "600"))
PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False").lower() == "true"
START_PIC = os.environ.get("START_PIC", "")

START_MSG = (
    "⚡ <b>Hey, {first} ~</b>\n\n"
    "<b>I AM A SIMPLE YET POWERFUL PRIVATE FILE SHARING BOT, "
    "SUPPORT REQUEST FORCESUB.</b>"
)
FORCE_MSG = (
    "⚠️ <b>Hey, {first} ~</b>\n\n"
    "<blockquote><b>You haven't joined {missing}/{total} channels yet. "
    "Please join the channels provided below, then try again..!</b></blockquote>\n\n"
    "❗ <b>Facing problems, use:</b> /help"
)
DELETE_MSG = (
    "⚠️ <b>Due to copyright issues....</b>\n\n"
    "<blockquote><b>Your files will be deleted within {time}. "
    "So please forward them to any other place for future availability.</b></blockquote>"
)
DELETED_MSG = (
    "<b>Previous message was deleted 🗑</b>\n\n"
    "<blockquote><b>If you want to get the files again, then click: "
    "[♻️ Click Here] button below else close this message.</b></blockquote>"
)
ABOUT_MSG = (
    "🤖 <b>Mʏ Nᴀᴍᴇ:</b> Fɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ V3 🤖\n"
    "◈ <b>Language:</b> Python 3\n"
    "◈ <b>Library:</b> Pyrogram v2\n"
    "◈ <b>Database:</b> MongoDB"\n
    "◈ <b>Dᴇᴠᴇʟᴏᴘᴇʀ:@Eren_157</b>"
)

HELP_TEXTS = {
    "help": "⚡ <b>INSTRUCTION FOR USING BOT</b>\n\n◈ Open a file link shared by the admins.\n◈ Join the required channels if asked, then press <b>Try Again</b>.\n◈ Files are auto deleted, so forward them quickly.",
    "users": "👀 <b>USER COMMANDS</b>\n\n/start - check alive / open file link\n/help - how to use the bot",
    "forcesub": "👀 <b>FORCESUB COMMANDS</b> (admins)\n\n/addfsub &lt;id&gt; [request] - add channel (max 6)\n/delfsub &lt;id&gt; - remove channel\n/fsubmode &lt;id&gt; normal|request - change mode\n/fsubs - list channels",
    "req_fsub": "⚙️ <b>REQUEST FORCESUB</b> (admins)\n\nAdd a channel with <code>/addfsub -100.. request</code> or switch with <code>/fsubmode -100.. request</code>.\nUsers who send a join request are treated as joined. Normal mode needs a real join.",
    "files": "⚙️ <b>MESSAGE/FILES SETTINGS</b> (admins)\n\nSend any file to get a link\n/genlink &lt;post link&gt; - single link\n/batch &lt;first&gt; &lt;last&gt; - batch link\n/setprotect on|off - protect content\n/broadcast - reply to a message",
    "auto_del": "⚙️ <b>AUTO DELETE SETTINGS</b> (admins)\n\n/setdelete &lt;seconds&gt; - set delete time (0 = off)\nDeletes are stored in the database, so they survive restarts.",
    "cmd": "⚠️ <b>BASIC ADMIN COMMANDS</b>\n\n/settings /stats /ban /unban /banned\n/addadmin /deladmin /admins (owner) /broadcast",
}

BOT_COMMANDS = [
    ("start", "Check alive/dead !"),
    ("help", "Instruction for using bot"),
    ("users", "View user setting commands"),
    ("forcesub", "View forcesub related commands"),
    ("req_fsub", "View request forcesub settings"),
    ("files", "View message/files related settings"),
    ("auto_del", "View auto delete settings"),
    ("cmd", "View basic bot commands (admins)"),
    ("restart", "Forcefully restart the bot (owner)"),
]
