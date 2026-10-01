import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "15055049"))
API_HASH = os.environ.get("API_HASH", "abe3f66fcd80c91e53009ba52c7b3a83")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8878678087:AAFjPiQn-Q_hYV5dT22NdgY9vB3IzLe0spg")

DB_URI = os.environ.get("DB_URI", "mongodb+srv://azeezbashaimran_db_user:F0NZSClydlcL2TBI@cluster0.sjw3p5j.mongodb.net/?appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "azeezbashaimran_db_user")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1003950444931"))

OWNER_ID = int(os.environ.get("OWNER_ID", "7653921320"))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x.lstrip("-").isdigit()]

MAX_FSUB = 6  # maximum force-sub channels
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "900"))
PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "False").lower() == "true"
START_PIC = os.environ.get("START_PIC", "https://ibb.co/gZRGmmxZ")

START_MSG = (
    "⚡ <b><blockquote>Hey, {first} ~</blockquote></b>\n\n"
    "<b><blockquote>I AM A SIMPLE YET POWERFUL PRIVATE FILE SHARING BOT, "
    "WORK FOR @Anime_Hub_Tamkl.</blockquote></b>"
)
FORCE_MSG = (
    "⚠️ <b>Hey, {first} ~</b>\n\n"
    "<blockquote><b>You haven't joined {missing}/{total} channels yet. "
    "Please join the channels provided below, then try again..!</b></blockquote>\n\n"
    "❗ <b>Facing problems, use:</b> /help"
)
DELETE_MSG = (
    "⚠️ <b>Dᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs....</b>\n\n"
    "<blockquote><b>ʏᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ {time}. "
    "sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ.</b></blockquote>"
)
DELETED_MSG = (
    "<b>Pʀᴇᴠɪᴏᴜs ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ 🗑</b>\n\n"
    "<blockquote><b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴀɢᴀɪɴ, ᴛʜᴇɴ ᴄʟɪᴄᴋ: "
    "[♻️ ᴄʟɪᴄᴋ ʜᴇʀᴇ] ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴇʟsᴇ ᴄʟᴏsᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.</b></blockquote>"
)
ABOUT_MSG = (
    "🤖 <b>Mʏ Nᴀᴍᴇ:</b> Fɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ V3 🤖\n"
    "◈ <b>Language:</b> Python 3\n"
    "◈ <b>Library:</b> Pyrogram v2\n"
    "◈ <b>Database:</b> MongoDB\n"
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
# ---------- shortener / verification ----------
MIN_VERIFY_TIME = int(os.environ.get("MIN_VERIFY_TIME", "60"))  # seconds, faster = bypass
VERIFY_HOURS = int(os.environ.get("VERIFY_HOURS", "12"))        # how long a user stays verified
TOKEN_EXPIRE = 600                                              # token valid for 10 minutes
VERIFY_PIC = os.environ.get("VERIFY_PIC", "")                   # optional image link

VERIFY_MSG = "Your Link is down here click on Short URL.."
VERIFIED_MSG = (
    "✅ <b>Verification successful!</b>\n\n"
    "<blockquote><b>You can now access files for the next {hours} hours.</b></blockquote>"
)
BYPASS_MSG = (
    "⚠️ <b>Bypass detected!</b>\n\n"
    "<blockquote><b>Please try again and complete the short link properly.</b></blockquote>"
)
EXPIRED_MSG = (
    "❌ <b>Verification link expired or invalid.</b>\n\n"
    "<blockquote><b>Please try again.</b></blockquote>"
)

BOT_COMMANDS += [
    ("shortener", "Shortener settings, on/off"),
    ("setshorturl", "Set shortener domain"),
    ("setshortapi", "Set shortener API key"),
    ("settutorial", "Set How to Open link"),
    ("setpremium", "Set Premium button link"),
    ("setverifytime", "Set verified hours"),
    ("setmintime", "Set bypass minimum seconds"),
]

HELP_TEXTS["cmd"] += (
    "\n\n🔗 <b>SHORTENER (admins)</b>\n"
    "/shortener - status | /shortener on | off\n"
    "/setshorturl &lt;domain&gt;\n/setshortapi &lt;api&gt;\n"
    "/settutorial &lt;link&gt;\n/setpremium &lt;link&gt;\n"
    "/setverifytime &lt;hours&gt;\n/setmintime &lt;seconds&gt;"
)
