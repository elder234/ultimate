from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aria2p import API as ariaAPI, Client as ariaClient
from asyncio import Lock
from dotenv import load_dotenv, dotenv_values
from logging import (
    getLogger,
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    info as log_info,
    warning as log_warning,
    ERROR,
)
from myjd import __version__ as jdv
from os import remove, path as ospath, environ
from pymongo import MongoClient
from pyrogram import Client as tgClient, enums, __version__ as prv
from qbittorrentapi import Client as qbClient
from socket import setdefaulttimeout
from subprocess import Popen, run, check_output
from time import time
from tzlocal import get_localzone
from uvloop import install

# from faulthandler import enable as faulthandler_enable
# faulthandler_enable()

install()
setdefaulttimeout(600)

getLogger("urllib3").setLevel(INFO)
getLogger("requests").setLevel(INFO)
getLogger("qbittorrentapi").setLevel(INFO)
getLogger("pyrogram").setLevel(ERROR)
getLogger("httpx").setLevel(ERROR)

botStartTime = time()

basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

LOGGER = getLogger(__name__)

load_dotenv("config.env", override=True)

Intervals = {"status": {}, "qb": "", "jd": "", "stopAll": False}
QbTorrents = {}
jd_downloads = {}
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []
GLOBAL_EXTENSION_FILTER = ["aria2", "!qB"]
user_data = {}
aria2_options = {}
qbit_options = {}
queued_dl = {}
queued_up = {}
non_queued_dl = set()
non_queued_up = set()
multi_tags = set()

class Version:
    ar = ""
    ff = ""
    ga = ""
    jd = ""
    jv = ""
    mg = ""
    p7 = ""
    pr = ""
    py = ""
    qb = ""
    rc = ""
    yt = ""

# Version Check
try:
    Version.ar = check_output(["chrome --v"], shell=True).decode().split("\n")[0].split(" ")[2]
except Exception as e:
    LOGGER.warning(f"Failed to get Aria2c version! ERROR: {e}")
try:
    Version.ff = check_output(["opera -version | grep 'ffmpeg version' | sed -e 's/ffmpeg version //' -e 's/[^0-9.].*//'"], shell=True).decode().replace("\n", "")
except Exception as e:
    LOGGER.warning(f"Failed to get FFMPEG version! ERROR: {e}")
try:
    Version.ga = check_output(["pip show google-api-python-client | grep Version"], shell=True).decode().split(" ", 1)[1].replace("\n", "")
except Exception as e:
    LOGGER.warning(f"Failed to get Google Api version! ERROR: {e}")
Version.jd = jdv
try:
    Version.jv = check_output(["safari --version"], shell=True).decode().split(" ")[1]
except Exception as e:
    LOGGER.warning(f"Failed to get Java version! ERROR: {e}")
try:
    Version.mg = check_output(["pip show megasdk | grep Version"], shell=True).decode().split(" ", 1)[1].replace("\n", "")
except Exception as e:
    LOGGER.warning(f"Failed to get MegaSDK version! ERROR: {e}")
try:
    Version.p7 = check_output(["7z | grep 7-Zip"], shell=True).decode().split(" ")[2]
except Exception as e:
    LOGGER.warning(f"Failed to get P7Zip version! ERROR: {e}")
Version.pr = prv
try:
    Version.py = check_output(["python --version"], shell=True).decode().split()[-1]
except Exception as e:
    LOGGER.warning(f"Failed to get Python version! ERROR: {e}")
try:
    Version.qb = check_output(["firefox --version"], shell=True).decode().split(" ", 1)[1].replace("\n", "")
except Exception as e:
    LOGGER.warning(f"Failed to get QBittorrent version! ERROR: {e}")
try:
    Version.rc = check_output(["edge --version"], shell=True).decode().split("\n")[0].split(" ")[1]
except Exception as e:
    LOGGER.warning(f"Failed to get RClone version! ERROR: {e}")
try:
    Version.yt = check_output(["yt-dlp --version"], shell=True).decode().split("\n")[0]
except Exception as e:
    LOGGER.warning(f"Failed to get YT-DLP version! ERROR: {e}")

try:
    if bool(environ.get("_____REMOVE_THIS_LINE_____")):
        log_error("The README.md file there to be read!")
        exit(1)
except:
    pass

task_dict_lock = Lock()
queue_dict_lock = Lock()
qb_listener_lock = Lock()
jd_lock = Lock()
cpu_eater_lock = Lock()
subprocess_lock = Lock()
status_dict = {}
task_dict = {}
rss_dict = {}

BOT_TOKEN = environ.get("BOT_TOKEN", "")
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN is not found!")
    exit(1)

bot_id = BOT_TOKEN.split(":", 1)[0]

DATABASE_URL = environ.get("DATABASE_URL", "")
if len(DATABASE_URL) == 0:
    DATABASE_URL = ""

if DATABASE_URL:
    try:
        conn = MongoClient(DATABASE_URL)
        db = conn.mltb
        current_config = dict(dotenv_values("config.env"))
        old_config = db.settings.deployConfig.find_one({"_id": bot_id})
        if old_config is None:
            db.settings.deployConfig.replace_one(
                {"_id": bot_id}, current_config, upsert=True
            )
        else:
            del old_config["_id"]
        if old_config and old_config != current_config:
            db.settings.deployConfig.replace_one(
                {"_id": bot_id}, current_config, upsert=True
            )
        elif config_dict := db.settings.config.find_one({"_id": bot_id}):
            del config_dict["_id"]
            for key, value in config_dict.items():
                environ[key] = str(value)
        if pf_dict := db.settings.files.find_one({"_id": bot_id}):
            del pf_dict["_id"]
            for key, value in pf_dict.items():
                if value:
                    file_ = key.replace("__", ".")
                    with open(file_, "wb+") as f:
                        f.write(value)
                    if file_ == "cfg.zip":
                        run(["rm", "-rf", "/JDownloader/cfg"])
                        run(["7z", "x", "cfg.zip", "-o/JDownloader"])
                        remove("cfg.zip")
        if a2c_options := db.settings.aria2c.find_one({"_id": bot_id}):
            del a2c_options["_id"]
            aria2_options = a2c_options
        if qbit_opt := db.settings.qbittorrent.find_one({"_id": bot_id}):
            del qbit_opt["_id"]
            qbit_options = qbit_opt
        conn.close()
        BOT_TOKEN = environ.get("BOT_TOKEN", "")
        bot_id = BOT_TOKEN.split(":", 1)[0]
        DATABASE_URL = environ.get("DATABASE_URL", "")
    except Exception as e:
        LOGGER.error(f"Database ERROR: {e}")
else:
    config_dict = {}

if not ospath.exists(".netrc"):
    with open(".netrc", "w"):
        pass
    
log_info("Set up Aria2c & QBittorrent...")
run(
    "chmod 600 .netrc && cp .netrc /root/.netrc && chmod +x aria-nox.sh && ./aria-nox.sh",
    shell=True,
)

OWNER_ID = environ.get("OWNER_ID", "")
if len(OWNER_ID) == 0:
    log_error("OWNER_ID is not found!")
    exit(1)
else:
    OWNER_ID = int(OWNER_ID)

TELEGRAM_API = environ.get("TELEGRAM_API", "")
if len(TELEGRAM_API) == 0:
    log_error("TELEGRAM_API is not found!")
    exit(1)
else:
    TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get("TELEGRAM_HASH", "")
if len(TELEGRAM_HASH) == 0:
    log_error("TELEGRAM_HASH is not found!")
    exit(1)

# Using different TELEGRAM_API  & TELEGRAM_HASH for USER_SESSION_STRING
TELEGRAM_API_PREMIUM = environ.get("TELEGRAM_API_PREMIUM", "")
TELEGRAM_HASH_PREMIUM = environ.get("TELEGRAM_HASH_PREMIUM", "")

GDRIVE_ID = environ.get("GDRIVE_ID", "")
if len(GDRIVE_ID) == 0:
    GDRIVE_ID = ""

RCLONE_PATH = environ.get("RCLONE_PATH", "")
if len(RCLONE_PATH) == 0:
    RCLONE_PATH = ""

RCLONE_FLAGS = environ.get("RCLONE_FLAGS", "")
if len(RCLONE_FLAGS) == 0:
    RCLONE_FLAGS = ""

DEFAULT_UPLOAD = environ.get("DEFAULT_UPLOAD", "")
if DEFAULT_UPLOAD != "rc":
    DEFAULT_UPLOAD = "gd"

DOWNLOAD_DIR = environ.get("DOWNLOAD_DIR", "")
if len(DOWNLOAD_DIR) == 0:
    DOWNLOAD_DIR = "/usr/src/app/downloads/"
elif not DOWNLOAD_DIR.endswith("/"):
    DOWNLOAD_DIR = f"{DOWNLOAD_DIR}/"

AUTHORIZED_CHATS = environ.get("AUTHORIZED_CHATS", "")
if len(AUTHORIZED_CHATS) != 0:
    aid = AUTHORIZED_CHATS.split()
    for id_ in aid:
        if ":" in id_:
            user_data[int(id_.split(":")[0].strip())] = {
                "thread_id": int(id_.split(":")[1].strip()), "is_auth": True}
        else:
            user_data[int(id_.strip())] = {"is_auth": True}

SUDO_USERS = environ.get("SUDO_USERS", "")
if len(SUDO_USERS) != 0:
    aid = SUDO_USERS.split()
    for id_ in aid:
        user_data[int(id_.strip())] = {"is_sudo": True}

EXTENSION_FILTER = environ.get("EXTENSION_FILTER", "")
if len(EXTENSION_FILTER) > 0:
    fx = EXTENSION_FILTER.split()
    for x in fx:
        x = x.lstrip(".")
        GLOBAL_EXTENSION_FILTER.append(x.strip().lower())

USER_SESSION_STRING = environ.get("USER_SESSION_STRING", "")
if len(USER_SESSION_STRING) != 0:
    log_info(f"Creating client from USER_SESSION_STRING ({USER_SESSION_STRING[:10]}***{USER_SESSION_STRING[-10:]})...")
    if len(TELEGRAM_API_PREMIUM) != 0 and len(TELEGRAM_HASH_PREMIUM) != 0:
        log_info("Using another Telegram Api & Telegram Hash for User Session...")
        TELEGRAM_API_PREMIUM = int(TELEGRAM_API_PREMIUM)
        user = tgClient(
            "user", 
            TELEGRAM_API_PREMIUM, 
            TELEGRAM_HASH_PREMIUM, 
            session_string=USER_SESSION_STRING,
            parse_mode=enums.ParseMode.HTML, 
            workers=100, 
            max_concurrent_transmissions=100
        ).start()
    else:
        user = tgClient(
            "user", 
            TELEGRAM_API, 
            TELEGRAM_HASH, 
            session_string=USER_SESSION_STRING,
            parse_mode=enums.ParseMode.HTML, 
            workers=100, 
            max_concurrent_transmissions=100
        ).start()
    IS_PREMIUM_USER = user.me.is_premium
else:
    user = ""
    IS_PREMIUM_USER = False
    
JD_EMAIL = environ.get("JD_EMAIL", "")
JD_PASS = environ.get("JD_PASS", "")
if len(JD_EMAIL) == 0 or len(JD_PASS) == 0:
    JD_EMAIL = ""
    JD_PASS = ""

MEGA_EMAIL = environ.get("MEGA_EMAIL", "")
MEGA_PASS = environ.get("MEGA_PASS", "")
if len(MEGA_EMAIL) == 0 or len(MEGA_PASS) == 0:
    MEGA_EMAIL= ""
    MEGA_PASS = ""

FILELION_API = environ.get("FILELION_API", "")
if len(FILELION_API) == 0:
    FILELION_API = ""

STREAMWISH_API = environ.get("STREAMWISH_API", "")
if len(STREAMWISH_API) == 0:
    STREAMWISH_API = ""

ALLDEBRID_API = environ.get("ALLDEBRID_API", "")
if len(ALLDEBRID_API) != 0:
    log_info("You're provided ALLDEBRID_API, Don't forget to auth in email before using this!")
else:
    ALLDEBRID_API = ""

DEBRIDLINK_API = environ.get("DEBRIDLINK_API", "")
if len(DEBRIDLINK_API) == 0:
    DEBRIDLINK_API = ""

INDEX_URL = environ.get("INDEX_URL", "").rstrip("/")
if len(INDEX_URL) == 0:
    INDEX_URL = ""

SEARCH_API_LINK = environ.get("SEARCH_API_LINK", "").rstrip("/")
if len(SEARCH_API_LINK) == 0:
    SEARCH_API_LINK = ""

LEECH_FILENAME_PREFIX = environ.get("LEECH_FILENAME_PREFIX", "")
if len(LEECH_FILENAME_PREFIX) == 0:
    LEECH_FILENAME_PREFIX = ""

SEARCH_PLUGINS = environ.get("SEARCH_PLUGINS", "")
if len(SEARCH_PLUGINS) == 0:
    SEARCH_PLUGINS = ""

MAX_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000
log_info(f"Max Split Size : {MAX_SPLIT_SIZE}")

LEECH_SPLIT_SIZE = environ.get("LEECH_SPLIT_SIZE", "")
if (
    len(LEECH_SPLIT_SIZE) == 0
    or int(LEECH_SPLIT_SIZE) > MAX_SPLIT_SIZE
    or LEECH_SPLIT_SIZE == "2097152000"
):
    LEECH_SPLIT_SIZE = MAX_SPLIT_SIZE
else:
    LEECH_SPLIT_SIZE = int(LEECH_SPLIT_SIZE)

STATUS_UPDATE_INTERVAL = environ.get("STATUS_UPDATE_INTERVAL", "")
if len(STATUS_UPDATE_INTERVAL) == 0:
    STATUS_UPDATE_INTERVAL = 15
else:
    STATUS_UPDATE_INTERVAL = int(STATUS_UPDATE_INTERVAL)

YT_DLP_OPTIONS = environ.get("YT_DLP_OPTIONS", "")
if len(YT_DLP_OPTIONS) == 0:
    YT_DLP_OPTIONS = ""

SEARCH_LIMIT = environ.get("SEARCH_LIMIT", "")
SEARCH_LIMIT = 0 if len(SEARCH_LIMIT) == 0 else int(SEARCH_LIMIT)

LEECH_CHAT_ID = environ.get("LEECH_CHAT_ID", "")
if len(LEECH_CHAT_ID) == 0:
    LEECH_CHAT_ID = ""

LOG_CHAT_ID = environ.get("LOG_CHAT_ID", "")
if len(LOG_CHAT_ID) == 0:
    LOG_CHAT_ID = ""

RSS_CHAT_ID = environ.get("RSS_CHAT_ID", "")
if len(RSS_CHAT_ID) == 0:
    RSS_CHAT_ID = ""

STATUS_LIMIT = environ.get("STATUS_LIMIT", "")
STATUS_LIMIT = 10 if len(STATUS_LIMIT) == 0 else int(STATUS_LIMIT)

RSS_DELAY = environ.get("RSS_DELAY", "")
RSS_DELAY = 600 if len(RSS_DELAY) == 0 else int(RSS_DELAY)

CMD_SUFFIX = environ.get("CMD_SUFFIX", "")

TORRENT_TIMEOUT = environ.get("TORRENT_TIMEOUT", "")
TORRENT_TIMEOUT = "" if len(TORRENT_TIMEOUT) == 0 else int(TORRENT_TIMEOUT)

QUEUE_ALL = environ.get("QUEUE_ALL", "")
QUEUE_ALL = "" if len(QUEUE_ALL) == 0 else int(QUEUE_ALL)

QUEUE_DOWNLOAD = environ.get("QUEUE_DOWNLOAD", "")
QUEUE_DOWNLOAD = "" if len(QUEUE_DOWNLOAD) == 0 else int(QUEUE_DOWNLOAD)

QUEUE_UPLOAD = environ.get("QUEUE_UPLOAD", "")
QUEUE_UPLOAD = "" if len(QUEUE_UPLOAD) == 0 else int(QUEUE_UPLOAD)

INCOMPLETE_TASK_NOTIFIER = environ.get("INCOMPLETE_TASK_NOTIFIER", "")
INCOMPLETE_TASK_NOTIFIER = INCOMPLETE_TASK_NOTIFIER.lower() == "true"

STOP_DUPLICATE = environ.get("STOP_DUPLICATE", "")
STOP_DUPLICATE = STOP_DUPLICATE.lower() == "true"

IS_TEAM_DRIVE = environ.get("IS_TEAM_DRIVE", "")
IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == "true"

USE_SERVICE_ACCOUNTS = environ.get("USE_SERVICE_ACCOUNTS", "")
USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == "true"

USE_TELEGRAPH = environ.get("USE_TELEGRAPH", "")
USE_TELEGRAPH = USE_TELEGRAPH.lower() == "true"

WEB_PINCODE = environ.get("WEB_PINCODE", "")
WEB_PINCODE = WEB_PINCODE.lower() == "true"

AS_DOCUMENT = environ.get("AS_DOCUMENT", "")
AS_DOCUMENT = AS_DOCUMENT.lower() == "true"

EQUAL_SPLITS = environ.get("EQUAL_SPLITS", "")
EQUAL_SPLITS = EQUAL_SPLITS.lower() == "true"

MEDIA_GROUP = environ.get("MEDIA_GROUP", "")
MEDIA_GROUP = MEDIA_GROUP.lower() == "true"

USER_TRANSMISSION = environ.get("USER_TRANSMISSION", "")
USER_TRANSMISSION = USER_TRANSMISSION.lower() == "true" and IS_PREMIUM_USER

IS_HEROKU = False
IS_RENDER = False

BASE_URL = environ.get("BASE_URL", "")
HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME", "")
RENDER_APP_NAME = environ.get("RENDER_APP_NAME", "")
if len(BASE_URL) == 0:
    if len(HEROKU_APP_NAME) != 0:
        IS_HEROKU = True

        if "://" in HEROKU_APP_NAME:
            BASE_URL = HEROKU_APP_NAME
        else:
            BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"

        log_info("Using HEROKU_APP_NAME as BASE_URL!")
        
    elif len(RENDER_APP_NAME) != 0:
        IS_RENDER = True
        
        if "://" in RENDER_APP_NAME:
            BASE_URL = RENDER_APP_NAME
        else:
            BASE_URL = f"https://{RENDER_APP_NAME}.onrender.com"

        log_info("Using RENDER_APP_NAME as BASE_URL!")
        
    else:
        BASE_URL = ""

BASE_URL = BASE_URL.rstrip("/")

BASE_URL_PORT = str(environ.get("PORT", ""))
if len(BASE_URL_PORT) == 0:
    BASE_URL_PORT = str(environ.get("BASE_URL_PORT", ""))
    if len(BASE_URL_PORT) == 0:
        BASE_URL_PORT = 80

BASE_URL_PORT = int(BASE_URL_PORT)

UPSTREAM_REPO = environ.get("UPSTREAM_REPO", "")
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = ""

UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH", "")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "master"

RCLONE_SERVE_URL = environ.get("RCLONE_SERVE_URL", "").rstrip("/")
if len(RCLONE_SERVE_URL) == 0:
    RCLONE_SERVE_URL = ""

RCLONE_SERVE_PORT = environ.get("RCLONE_SERVE_PORT", "")
RCLONE_SERVE_PORT = 8080 if len(
    RCLONE_SERVE_PORT) == 0 else int(RCLONE_SERVE_PORT)

RCLONE_SERVE_USER = environ.get("RCLONE_SERVE_USER", "")
if len(RCLONE_SERVE_USER) == 0:
    RCLONE_SERVE_USER = ""

RCLONE_SERVE_PASS = environ.get("RCLONE_SERVE_PASS", "")
if len(RCLONE_SERVE_PASS) == 0:
    RCLONE_SERVE_PASS = ""

NAME_SUBSTITUTE = environ.get("NAME_SUBSTITUTE", "")
NAME_SUBSTITUTE = "" if len(NAME_SUBSTITUTE) == 0 else NAME_SUBSTITUTE

MIXED_LEECH = environ.get("MIXED_LEECH", "")
MIXED_LEECH = MIXED_LEECH.lower() == "true" and IS_PREMIUM_USER

config_dict = {
    "ALLDEBRID_API": ALLDEBRID_API,
    "AS_DOCUMENT": AS_DOCUMENT,
    "AUTHORIZED_CHATS": AUTHORIZED_CHATS,
    "BASE_URL_PORT": BASE_URL_PORT,
    "BASE_URL": BASE_URL,
    "BOT_TOKEN": BOT_TOKEN,
    "CMD_SUFFIX": CMD_SUFFIX,
    "DATABASE_URL": DATABASE_URL,
    "DEBRIDLINK_API": DEBRIDLINK_API,
    "DEFAULT_UPLOAD": DEFAULT_UPLOAD,
    "DOWNLOAD_DIR": DOWNLOAD_DIR,
    "EQUAL_SPLITS": EQUAL_SPLITS,
    "EXTENSION_FILTER": EXTENSION_FILTER,
    "FILELION_API": FILELION_API,
    "GDRIVE_ID": GDRIVE_ID,
    "INCOMPLETE_TASK_NOTIFIER": INCOMPLETE_TASK_NOTIFIER,
    "INDEX_URL": INDEX_URL,
    "IS_TEAM_DRIVE": IS_TEAM_DRIVE,
    "JD_EMAIL": JD_EMAIL,
    "JD_PASS": JD_PASS,
    "LEECH_CHAT_ID": LEECH_CHAT_ID,
    "LEECH_FILENAME_PREFIX": LEECH_FILENAME_PREFIX,
    "LEECH_SPLIT_SIZE": LEECH_SPLIT_SIZE,
    "LOG_CHAT_ID": LOG_CHAT_ID,
    "MEDIA_GROUP": MEDIA_GROUP,
    "MEGA_EMAIL": MEGA_EMAIL,
    "MEGA_PASS": MEGA_PASS,
    "MIXED_LEECH": MIXED_LEECH,
    "NAME_SUBSTITUTE": NAME_SUBSTITUTE,
    "OWNER_ID": OWNER_ID,
    "QUEUE_ALL": QUEUE_ALL,
    "QUEUE_DOWNLOAD": QUEUE_DOWNLOAD,
    "QUEUE_UPLOAD": QUEUE_UPLOAD,
    "RCLONE_FLAGS": RCLONE_FLAGS,
    "RCLONE_PATH": RCLONE_PATH,
    "RCLONE_SERVE_PASS": RCLONE_SERVE_PASS,
    "RCLONE_SERVE_PORT": RCLONE_SERVE_PORT,
    "RCLONE_SERVE_URL": RCLONE_SERVE_URL,
    "RCLONE_SERVE_USER": RCLONE_SERVE_USER,
    "RSS_CHAT_ID": RSS_CHAT_ID,
    "RSS_DELAY": RSS_DELAY,
    "SEARCH_API_LINK": SEARCH_API_LINK,
    "SEARCH_LIMIT": SEARCH_LIMIT,
    "SEARCH_PLUGINS": SEARCH_PLUGINS,
    "STATUS_LIMIT": STATUS_LIMIT,
    "STATUS_UPDATE_INTERVAL": STATUS_UPDATE_INTERVAL,
    "STOP_DUPLICATE": STOP_DUPLICATE,
    "STREAMWISH_API": STREAMWISH_API,
    "SUDO_USERS": SUDO_USERS,
    "TELEGRAM_API_PREMIUM": TELEGRAM_API_PREMIUM,
    "TELEGRAM_API": TELEGRAM_API,
    "TELEGRAM_HASH_PREMIUM": TELEGRAM_HASH_PREMIUM,
    "TELEGRAM_HASH": TELEGRAM_HASH,
    "TORRENT_TIMEOUT": TORRENT_TIMEOUT,
    "UPSTREAM_BRANCH": UPSTREAM_BRANCH,
    "UPSTREAM_REPO": UPSTREAM_REPO,
    "USE_SERVICE_ACCOUNTS": USE_SERVICE_ACCOUNTS,
    "USE_TELEGRAPH": USE_TELEGRAPH,
    "USER_SESSION_STRING": USER_SESSION_STRING,
    "USER_TRANSMISSION": USER_TRANSMISSION,
    "WEB_PINCODE": WEB_PINCODE,
    "YT_DLP_OPTIONS": YT_DLP_OPTIONS,
}

# Reminder if forgot set something ^^
for item, value in config_dict.items():
    if (
        isinstance(value, str)
        and len(value) == 0
    ):
        log_warning(f"{item} is not found!")

if GDRIVE_ID:
    DRIVES_NAMES.append("Main")
    DRIVES_IDS.append(GDRIVE_ID)
    INDEX_URLS.append(INDEX_URL)

if ospath.exists("list_drives.txt"):
    with open("list_drives.txt", "r+") as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            DRIVES_IDS.append(temp[1])
            DRIVES_NAMES.append(temp[0].replace("_", " "))
            if len(temp) > 2:
                INDEX_URLS.append(temp[2])
            else:
                INDEX_URLS.append("")

log_info("Set up Web Server...")
Popen(
    f"gunicorn web.wserver:app --bind 0.0.0.0:{BASE_URL_PORT} --worker-class gevent", 
    shell=True
    )

log_info("Set up Service Accounts...")
if ospath.exists("accounts.zip"):
    if ospath.exists("accounts"):
        run(["rm", "-rf", "accounts"])
    run(["7z", "x", "-o.", "-aoa", "accounts.zip", "accounts/*.json"])
    run(["chmod", "-R", "777", "accounts"])
    remove("accounts.zip")
if not ospath.exists("accounts"):
    log_warning("Service Accounts is not found!")
    config_dict["USE_SERVICE_ACCOUNTS"] = False

def get_qb_client():
    return qbClient(
        host="localhost", 
        port=8090, 
        # username="admin",
        # password="adminadmin",
        FORCE_SCHEME_FROM_HOST=False, 
        VERIFY_WEBUI_CERTIFICATE=False, 
        REQUESTS_ARGS={"timeout": (30, 60)}
    )

aria2c_global = [
    "bt-max-open-files", 
    "download-result", 
    "keep-unfinished-download-result",
    "log", 
    "log-level",
    "max-concurrent-downloads",
    "max-download-result", 
    "max-overall-download-limit", 
    "save-session",
    "max-overall-upload-limit", 
    "optimize-concurrent-downloads", 
    "save-cookies", 
    "server-stat-of"
]

log_info(f"Creating client from BOT_TOKEN ({BOT_TOKEN[:10]}***{BOT_TOKEN[-10:]})...")
bot = tgClient(
    "bot", 
    TELEGRAM_API, 
    TELEGRAM_HASH,
    bot_token=BOT_TOKEN, 
    parse_mode=enums.ParseMode.HTML, 
    workers=1000, 
    max_concurrent_transmissions=100
).start()

bot_loop = bot.loop
bot_name = bot.me.username

scheduler = AsyncIOScheduler(timezone=str(
    get_localzone()), event_loop=bot_loop)

if not qbit_options:
    qbit_options = dict(get_qb_client().app_preferences())
    del qbit_options["listen_port"]
    for k in list(qbit_options.keys()):
        if k.startswith("rss"):
            del qbit_options[k]
else:
    qb_opt = {**qbit_options}
    for k, v in list(qb_opt.items()):
        if v in ["", "*"]:
            del qb_opt[k]
    get_qb_client().app_set_preferences(qb_opt)

aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))
if not aria2_options:
    aria2_options = aria2.client.get_global_option()
else:
    a2c_glo = {op: aria2_options[op] for op in aria2c_global if op in aria2_options}
    aria2.set_global_options(a2c_glo)

log_info("Set up auto Alive...")
Popen(["python3", "alive.py"])
