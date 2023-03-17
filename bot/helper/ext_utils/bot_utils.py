#!/usr/bin/env python3
from re import match as re_match
from time import time
from math import ceil
from html import escape
from psutil import virtual_memory, cpu_percent, disk_usage, net_io_counters
from requests import head as rhead
from urllib.request import urlopen
from asyncio import create_subprocess_exec, create_subprocess_shell, run_coroutine_threadsafe, sleep
from asyncio.subprocess import PIPE
from functools import partial, wraps
from concurrent.futures import ThreadPoolExecutor

from bot import download_dict, download_dict_lock, botStartTime, DOWNLOAD_DIR, user_data, config_dict, bot_loop
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker

MAGNET_REGEX = r'magnet:\?xt=urn:(btih|btmh):[a-zA-Z0-9]*\s*'

URL_REGEX = r'^(?!\/)(rtmps?:\/\/|mms:\/\/|rtsp:\/\/|https?:\/\/|ftp:\/\/)?([^\/:]+:[^\/@]+@)?(www\.)?(?=[^\/:\s]+\.[^\/:\s]+)([^\/:\s]+\.[^\/:\s]+)(:\d+)?(\/[^#\s]*[\s\S]*)?(\?[^#\s]*)?(#.*)?$'

COUNT = 0
PAGE_NO = 1
PAGES = 0


class MirrorStatus:
    STATUS_UPLOADING = "Mengunggah..."
    STATUS_DOWNLOADING = "Mengunduh..."
    STATUS_CLONING = "Mengclone..."
    STATUS_QUEUEDL = "Menunggu antrian download..."
    STATUS_QUEUEUP = "Menunggu antrian upload..."
    STATUS_PAUSED = "Dihentikan."
    STATUS_ARCHIVING = "Mengarsip..."
    STATUS_EXTRACTING = "Mengekstrak..."
    STATUS_SPLITTING = "Membagi..."
    STATUS_CHECKING = "Mengecek..."
    STATUS_SEEDING = "Mengeseed..."


SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = False
        bot_loop.create_task(self.__setInterval())

    async def __setInterval(self):
        nextTime = time() + self.interval
        while not self.stopEvent:
            await sleep(nextTime - time())
            if self.stopEvent:
                break
            await self.action()
            nextTime = time() + self.interval

    def cancel(self):
        self.stopEvent = True


def get_readable_file_size(size_in_bytes):
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'


async def getDownloadByGid(gid):
    async with download_dict_lock:
        for dl in list(download_dict.values()):
            if dl.gid() == gid:
                return dl
    return None


async def getAllDownload(req_status):
    async with download_dict_lock:
        for dl in list(download_dict.values()):
            status = dl.status()
            if req_status in ['all', status]:
                return dl
    return None


def bt_selection_buttons(id_):
    gid = id_[:12] if len(id_) > 20 else id_
    pincode = ""
    for n in id_:
        if n.isdigit():
            pincode += str(n)
        if len(pincode) == 4:
            break

    buttons = ButtonMaker()
    BASE_URL = config_dict['BASE_URL']
    if config_dict['WEB_PINCODE']:
        buttons.ubutton("Select Files", f"{BASE_URL}/app/files/{id_}")
        buttons.ibutton("Pincode", f"btsel pin {gid} {pincode}")
    else:
        buttons.ubutton(
            "Select Files", f"{BASE_URL}/app/files/{id_}?pin_code={pincode}")
    buttons.ibutton("Done Selecting", f"btsel done {gid} {id_}")
    return buttons.build_menu(2)


def get_progress_bar_string(pct):
    pct = float(pct.split('%')[0])
    p = min(max(pct, 0), 100)
    cFull = int(p // 8)
    p_str = '■' * cFull
    p_str += '□' * (12 - cFull)
    return f"[{p_str}]"


def get_readable_message():
    msg = ""
    button = None
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    tasks = len(download_dict)
    globals()['PAGES'] = ceil(tasks/STATUS_LIMIT)
    if PAGE_NO > PAGES and PAGES != 0:
        globals()['COUNT'] -= STATUS_LIMIT
        globals()['PAGE_NO'] -= 1
    for download in list(download_dict.values())[COUNT:STATUS_LIMIT+COUNT]:
        msg += f"<code>{escape(str(download.name()))}</code>"
        if download.status() not in [MirrorStatus.STATUS_SPLITTING, MirrorStatus.STATUS_SEEDING]:
            msg += f"\n<b>┌┤ {get_progress_bar_string(download.progress())} {download.progress()} ├┐</b>"
            if download.message.chat.type.name in ['SUPERGROUP', 'CHANNEL']:
                msg += f"\n<b>├ Status:</b> <a href='{download.message.link}'>{download.status()}</a>"
            else:
                msg += f"\n<b>├ Status:</b> {download.status()}"
            msg += f"\n<b>├ Proses:</b> {download.processed_bytes()} dari {download.size()}"
            msg += f"\n<b>├ Kecepatan:</b> {download.speed()} | <b>ETA:</b> {download.eta()}"
            if hasattr(download, 'seeders_num'):
                try:
                    msg += f"\n<b>├ Seeders:</b> {download.seeders_num()} | <b>Leechers:</b> {download.leechers_num()}"
                except:
                    pass
        elif download.status() == MirrorStatus.STATUS_SEEDING:
            msg += "┌┤ 🆂🅴🅴🅳🅸🅽🅶 ├┐"
            if download.message.chat.type.name in ['SUPERGROUP', 'CHANNEL']:
                msg += f"\n<b>├ Status:</b> <a href='{download.message.link}'>{download.status()}</a>"
            else:
                msg += f"\n<b>├ Status:</b> {download.status()}"
            msg += f"\n<b>├ Ukuran: </b>{download.size()}"
            msg += f"\n<b>├ Kecepatan: </b>{download.upload_speed()}"
            msg += f" | <b>Diupload: </b>{download.uploaded_bytes()}"
            msg += f"\n<b>├ Ratio: </b>{download.ratio()}"
            msg += f" | <b>Waktu: </b>{download.seeding_time()}"
        else:
            msg += f"\n<b>├ Ukuran: </b>{download.size()}"
        if download.message.from_user.username:
            msg += f"\n<b>├ User:</b> <a href='https://t.me/{download.message.from_user.username}'>{download.message.from_user.first_name}</a>"
            msg += f" | <b>ID:</b> <code>{download.message.from_user.id}</code>"
        else:
            msg += f"\n<b>├ User:</b> {download.message.from_user.first_name}</a>"
            msg += f" | <b>ID:</b> <code>{download.message.from_user.id}</code>"
        msg += f"\n<b>└</b> <code>/{BotCommands.CancelMirror[0]} {download.gid()}</code>\n\n"
    if len(msg) == 0:
        return None, None
    dl_speed = 0
    up_speed = 0
    for download in list(download_dict.values()):
        if download.status() == MirrorStatus.STATUS_DOWNLOADING:
            spd = download.speed()
            if 'K' in spd:
                dl_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                dl_speed += float(spd.split('M')[0]) * 1048576
        elif download.status() == MirrorStatus.STATUS_UPLOADING:
            spd = download.speed()
            if 'KB/s' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'MB/s' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
        elif download.status() == MirrorStatus.STATUS_SEEDING:
            spd = download.upload_speed()
            if 'K' in spd:
                up_speed += float(spd.split('K')[0]) * 1024
            elif 'M' in spd:
                up_speed += float(spd.split('M')[0]) * 1048576
    if tasks > STATUS_LIMIT:
        msg += f"<b>Halaman:</b> {PAGE_NO}/{PAGES} | <b>Tugas:</b> {tasks}\n"
        buttons = ButtonMaker()
        buttons.ibutton("⏪", "status pre")
        buttons.ibutton("⏩", "status nex")
        buttons.ibutton("♻️", "status ref")
        button = buttons.build_menu(3)
    msg += f"\n<b>🅳🅻:</b> {get_readable_file_size(dl_speed)}/s | <b>🆄🅻:</b> {get_readable_file_size(up_speed)}/s"
    msg += f"\n<b>🆃🅳🅻:</b> {get_readable_file_size(net_io_counters().bytes_recv)} | <b>🆃🆄🅻:</b> {get_readable_file_size(net_io_counters().bytes_sent)}"
    msg += f"\n<b>🅲🄿🆄:</b> {cpu_percent()}% | <b>🅳🅸🆂🅺:</b> {get_readable_file_size(disk_usage(DOWNLOAD_DIR).free)}"
    msg += f"\n<b>🆁🄰🅼:</b> {virtual_memory().percent}% | <b>🆃🅸🅼🅴:</b> {get_readable_time(time() - botStartTime)}"

    return msg, button


async def turn(data):
    STATUS_LIMIT = config_dict['STATUS_LIMIT']
    try:
        global COUNT, PAGE_NO
        async with download_dict_lock:
            if data[1] == "nex":
                if PAGE_NO == PAGES:
                    COUNT = 0
                    PAGE_NO = 1
                else:
                    COUNT += STATUS_LIMIT
                    PAGE_NO += 1
            elif data[1] == "pre":
                if PAGE_NO == 1:
                    COUNT = STATUS_LIMIT * (PAGES - 1)
                    PAGE_NO = PAGES
                else:
                    COUNT -= STATUS_LIMIT
                    PAGE_NO -= 1
        return True
    except:
        return False


def get_readable_time(seconds):
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def is_magnet(url):
    magnet = re_match(MAGNET_REGEX, url)
    return bool(magnet)


def is_url(url):
    url = re_match(URL_REGEX, url)
    return bool(url)


def is_gdrive_link(url):
    return "drive.google.com" in url


def is_share_link(url):
    return bool(re_match(r'https?:\/\/.+\.gdtot\.\S+|https?:\/\/(filepress|filebee|appdrive|gdflix)\.\S+', url))


def is_mega_link(url):
    return "mega.nz" in url or "mega.co.nz" in url


def is_rclone_path(path):
    return bool(re_match(r'^(mrcc:)?(?!magnet:)(?![- ])[a-zA-Z0-9_\. -]+(?<! ):(?!.*\/\/).+$|^rcd$', path))


def get_mega_link_type(url):
    if "folder" in url:
        return "folder"
    elif "file" in url:
        return "file"
    elif "/#F!" in url:
        return "folder"
    return "file"


def get_content_type(link):
    try:
        res = rhead(link, allow_redirects=True, timeout=5,
                    headers={'user-agent': 'Wget/1.12'})
        content_type = res.headers.get('content-type')
    except:
        try:
            res = urlopen(link, timeout=5)
            content_type = res.info().get_content_type()
        except:
            content_type = None
    return content_type


def update_user_ldata(id_, key, value):
    if id_ in user_data:
        user_data[id_][key] = value
    else:
        user_data[id_] = {key: value}


async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await create_subprocess_shell(cmd, stdout=PIPE, stderr=PIPE)
    else:
        proc = await create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    return stdout, stderr, proc.returncode


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return bot_loop.create_task(func(*args, **kwargs))
    return wrapper


async def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    with ThreadPoolExecutor() as pool:
        future = bot_loop.run_in_executor(pool, pfunc)
        return await future if wait else future


def async_to_sync(func, *args, wait=True, **kwargs):
    future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
    return future.result() if wait else future


def new_thread(func):
    @wraps(func)
    def wrapper(*args, wait=False, **kwargs):
        future = run_coroutine_threadsafe(func(*args, **kwargs), bot_loop)
        return future.result() if wait else future
    return wrapper
