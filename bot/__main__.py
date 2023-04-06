#!/usr/bin/env python3
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from os import execl as osexecl
from psutil import disk_usage, cpu_percent, cpu_count, virtual_memory, net_io_counters, boot_time, cpu_freq
from time import time
from sys import executable
from pyrogram.handlers import MessageHandler
from pyrogram.filters import command
from asyncio import create_subprocess_exec, gather
from subprocess import check_output
from quoters import Quote
from pytz import timezone
from datetime import datetime

from bot import bot, botStartTime, LOGGER, Interval, DATABASE_URL, user, QbInterval, INCOMPLETE_TASK_NOTIFIER, scheduler
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, cmd_exec, sync_to_async
from .helper.ext_utils.db_handler import DbManger
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from bot.helper.listeners.aria2_listener import start_aria2_listener
from .modules import authorize, clone, gd_count, gd_delete, gd_list, cancel_mirror, mirror_leech, status, torrent_search, torrent_select, ytdlp, rss, shell, eval, users_settings, bot_settings

start_aria2_listener()


def get_quotes():
    try:
        quotez = str(Quote.print_series_quote())
        quote = quotez.split(": ")[1]
        oleh = quotez.split(":")[0]
        quotes = f"{quote}\n~{oleh}"
    except:
        quotes = "Ngga ada Quote bijak buatmu wahai Tuan yang bijaksana :D"
    return quotes


def progress_bar(percentage):
    if isinstance(percentage, str):
        return 'NaN'
    try:
        percentage = int(percentage)
    except:
        percentage = 0
    return ''.join(
        '■' if i <= percentage // 10 else '□' for i in range(1, 11)
    )


async def stats(client, message):
    if await aiopath.exists('.git'):
        last_commit = await cmd_exec("git log -1 --date=short --pretty=format:'%cd <b>From</b> %cr'", True)
        last_commit = last_commit[0]
    else:
        last_commit = 'No UPSTREAM_REPO'
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    total, used, free, disk = disk_usage('/')
    try:
        total = get_readable_file_size(total)
    except:
        total = 'n/a'
    try:
        used = get_readable_file_size(used)
    except:
        used = 'n/a'
    try:
        free = get_readable_file_size(free)
    except:
        free = 'n/a'
    # Net Usage
    try:
        sent = get_readable_file_size(net_io_counters().bytes_sent)
    except:
        sent = 'n/a'
    try:
        recv = get_readable_file_size(net_io_counters().bytes_recv)
    except:
        recv = 'n/a'
    # Cpu
    cpuUsage = cpu_percent(interval=0.5)
    try:
        p_core = cpu_count(logical=False)
    except:
        p_core = 'n/a'
    try:
        t_core = cpu_count(logical=True)
    except:
        t_core = 'n/a'
    try:
        cpufreq = cpu_freq()
    except:
        cpufreq = 'n/a'
    try:
        freqcurrent = round(cpufreq.current)
    except:
        freqcurrent = 'n/a'
    memory = virtual_memory()
    mem_p = memory.percent
    try:
        mem_t = get_readable_file_size(memory.total)
    except:
        mem_t = 'n/a'
    try:
        mem_a = get_readable_file_size(memory.available)
    except:
        mem_a = 'n/a'
    try:
        mem_u = get_readable_file_size(memory.used)
    except:
        mem_u = 'n/a'
    # Neofetch
    neofetch = check_output(
        ["neofetch --shell_version off --stdout"], shell=True).decode()
    stats = f'<b>System</b>\n' \
            f'<code>{neofetch}</code>' \
            f'<b>CPU</b>\n' \
            f'<b>Cores:</b> <code>{p_core}</code>\n' \
            f'<b>Logical:</b> <code>{t_core}</code>\n' \
            f'<b>Frequency:</b> <code>{freqcurrent}</code>\n' \
            f'<code>[{progress_bar(cpuUsage)}] {cpuUsage}%</code>\n\n' \
            f'<b>RAM</b>\n' \
            f'<b>Terpakai:</b> <code>{mem_u}</code>\n' \
            f'<b>Tersedia:</b> <code>{mem_a}</code>\n' \
            f'<b>Total:</b> <code>{mem_t}</code>\n' \
            f'<code>[{progress_bar(mem_p)}] {mem_p}%</code>\n\n' \
            f'<b>Storage</b>\n' \
            f'<b>Terpakai:</b> <code>{used}</code>\n' \
            f'<b>Tersedia:</b> <code>{free}</code>\n' \
            f'<b>Total:</b> <code>{total}</code>\n' \
            f'<code>[{progress_bar(disk)}] {disk}%</code>\n\n' \
            f'<b>Network</b>\n'\
            f'<b>Download:</b> <code>{recv}</code>\n' \
            f'<b>Upload:</b> <code>{sent}</code>\n\n' \
            f'<b>Other</b>\n'\
            f'<b>Uptime:</b> <code>{currentTime}</code>\n' \
            f'<b>OS Uptime:</b> <code>{osUptime}</code>\n' \
            f'<b>Updated:</b> <code>{last_commit}</code>\n\n'
    stats += f'<b>Quotes Today:</b>\n' \
             f'<code>{get_quotes()}</code>\n'
    await sendMessage(message, stats)


async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(
        "Owner", "https://t.me/save_usdt")
    buttons.ubutton("Group", "https://t.me/arakurumi")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(client, message):
        start_string = f'''
Mirror Tautan Lambat menjadi Tautan Cepat!

Note:
Selalu backup File setelah Mirror untuk menghindari Team Drive kebanned!

Ketik /{BotCommands.HelpCommand} untuk mendapatkan list perintah yang tersedia
'''
        await sendMessage(message, start_string, reply_markup)
    else:
        await sendMessage(message, 'Bukan User yang diautorisasi!\nGabung grup untuk menggunakan Bot!', reply_markup)


async def restart(client, message):
    restart_message = await sendMessage(message, "Restarting...")
    if scheduler.running:
        scheduler.shutdown(wait=False)
    for interval in [QbInterval, Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    proc1 = await create_subprocess_exec('pkill', '-9', '-f', 'gunicorn|chrome|firefox|opera|rclone')
    proc2 = await create_subprocess_exec('python3', 'update.py')
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(client, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, "Mengetest waktu respon bot...")
    end_time = int(round(time() * 1000))
    await editMessage(reply, f'🤖 <b>Respon Bot:</b> <code>{end_time - start_time} ms</code>')


async def log(client, message):
    await sendFile(message, 'log.txt')

help_string = f'''
/{BotCommands.MirrorCommand[0]} or /{BotCommands.MirrorCommand[1]}: Start mirroring to Google Drive.
/{BotCommands.ZipMirrorCommand[0]} or /{BotCommands.ZipMirrorCommand[1]}: Start mirroring and upload the file/folder compressed with zip extension.
/{BotCommands.UnzipMirrorCommand[0]} or /{BotCommands.UnzipMirrorCommand[1]}: Start mirroring and upload the file/folder extracted from any archive extension.
/{BotCommands.QbMirrorCommand[0]} or /{BotCommands.QbMirrorCommand[1]}: Start Mirroring to Google Drive using qBittorrent.
/{BotCommands.QbZipMirrorCommand[0]} or /{BotCommands.QbZipMirrorCommand[1]}: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension.
/{BotCommands.QbUnzipMirrorCommand[0]} or /{BotCommands.QbUnzipMirrorCommand[1]}: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension.
/{BotCommands.YtdlCommand[0]} or /{BotCommands.YtdlCommand[1]}: Mirror yt-dlp supported link.
/{BotCommands.YtdlZipCommand[0]} or /{BotCommands.YtdlZipCommand[1]}: Mirror yt-dlp supported link as zip.
/{BotCommands.LeechCommand[0]} or /{BotCommands.LeechCommand[1]}: Start leeching to Telegram.
/{BotCommands.ZipLeechCommand[0]} or /{BotCommands.ZipLeechCommand[1]}: Start leeching and upload the file/folder compressed with zip extension.
/{BotCommands.UnzipLeechCommand[0]} or /{BotCommands.UnzipLeechCommand[1]}: Start leeching and upload the file/folder extracted from any archive extension.
/{BotCommands.QbLeechCommand[0]} or /{BotCommands.QbLeechCommand[1]}: Start leeching using qBittorrent.
/{BotCommands.QbZipLeechCommand[0]} or /{BotCommands.QbZipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder compressed with zip extension.
/{BotCommands.QbUnzipLeechCommand[0]} or /{BotCommands.QbUnzipLeechCommand[1]}: Start leeching using qBittorrent and upload the file/folder extracted from any archive extension.
/{BotCommands.YtdlLeechCommand[0]} or /{BotCommands.YtdlLeechCommand[1]}: Leech yt-dlp supported link.
/{BotCommands.YtdlZipLeechCommand[0]} or /{BotCommands.YtdlZipLeechCommand[1]}: Leech yt-dlp supported link as zip.
/{BotCommands.CloneCommand[0]} or /{BotCommands.CloneCommand[1]} [drive_url]: Copy file/folder to Google Drive.
/{BotCommands.CountCommand[0]} or /{BotCommands.CountCommand[1]} [drive_url]: Count file/folder of Google Drive.
/{BotCommands.DeleteCommand[0]} or /{BotCommands.DeleteCommand[1]} [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo).
/{BotCommands.UserSetCommand[0]} or /{BotCommands.UserSetCommand[1]} [query]: Users settings.
/{BotCommands.BotSetCommand[0]} or /{BotCommands.BotSetCommand[1]} [query]: Bot settings.
/{BotCommands.BtSelectCommand[0]} or /{BotCommands.BtSelectCommand[1]}: Select files from torrents by gid or reply.
/{BotCommands.CancelMirror[0]} or /{BotCommands.CancelMirror[1]}: Cancel task by gid or reply.
/{BotCommands.CancelAllCommand[0]} or /{BotCommands.CancelAllCommand[1]}  [query]: Cancel all [status] tasks.
/{BotCommands.ListCommand[0]} or /{BotCommands.ListCommand[1]} [query]: Search in Google Drive(s).
/{BotCommands.SearchCommand[0]} or /{BotCommands.SearchCommand[1]} [query]: Search for torrents with API.
/{BotCommands.StatusCommand[0]} or /{BotCommands.StatusCommand[1]}: Shows a status of all the downloads.
/{BotCommands.StatsCommand[0]} or /{BotCommands.StatsCommand[1]}: Show stats of the machine where the bot is hosted in.
/{BotCommands.PingCommand[0]} or /{BotCommands.PingCommand[1]}: Check how long it takes to Ping the Bot (Only Owner & Sudo).
/{BotCommands.AuthorizeCommand[0]} or /{BotCommands.AuthorizeCommand[1]}: Authorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UnAuthorizeCommand[0]} or /{BotCommands.UnAuthorizeCommand[1]}: Unauthorize a chat or a user to use the bot (Only Owner & Sudo).
/{BotCommands.UsersCommand[0]} or /{BotCommands.UsersCommand[1]}: show users settings (Only Owner & Sudo).
/{BotCommands.AddSudoCommand[0]} or /{BotCommands.AddSudoCommand[1]}: Add sudo user (Only Owner).
/{BotCommands.RmSudoCommand[0]} or /{BotCommands.RmSudoCommand[1]}: Remove sudo users (Only Owner).
/{BotCommands.RestartCommand[0]} or /{BotCommands.RestartCommand[1]}: Restart and update the bot (Only Owner & Sudo).
/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).
/{BotCommands.ShellCommand}: Run shell commands (Only Owner).
/{BotCommands.EvalCommand}: Run Python Code Line | Lines (Only Owner).
/{BotCommands.ExecCommand}: Run Commands In Exec (Only Owner).
/{BotCommands.ClearLocalsCommand}: Clear {BotCommands.EvalCommand} or {BotCommands.ExecCommand} locals (Only Owner).
/{BotCommands.RssCommand}: RSS Menu.

NOTE: Kirim perintah tanpa argument untuk melihat details perintah!
'''


async def bot_help(client, message):
    await sendMessage(message, help_string)


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith('Restarted Successfully!'):
                await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg)
                await aioremove(".restartmsg")
            else:
                await bot.send_message(chat_id=cid, text=msg, disable_web_page_preview=True,
                                       disable_notification=True)
        except Exception as e:
            LOGGER.error(e)

    now = datetime.now(timezone(f'Asia/Jakarta'))
    date = now.strftime('%d/%m/%y')
    time = now.strftime('%I:%M:%S %p')
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManger().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                msg = 'Restarted Successfully!' if cid == chat_id else 'Bot Restarted!'
                msg += f"\n<b>Waktu :</b> <code>{time}</code>"
                msg += f"\n<b>Tanggal :</b> <code>{date}</code>"
                msg += f"\n<b>Quotes Today :</b>"
                msg += f"\n<code>{get_quotes()}</code>"
                if data.items():
                    msg += f"\n\n<b>Tugas yang belum selesai :</b>"
                for tag, links in data.items():
                    msg += f"\n{tag} :"
                    for index, link in enumerate(links, start=1):
                        msg += f"\n <a href='{link}'>Tugas ke {index}</a>"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ''
                if msg:
                    await send_incompelete_task_message(cid, msg)

    if await aiopath.isfile(".restartmsg"):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text='Restarted Successfully!')
        except:
            pass
        await aioremove(".restartmsg")


async def main():
    await gather(start_cleanup(), torrent_search.initiate_search_tools(), restart_notification())

    bot.add_handler(MessageHandler(
        start, filters=command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(log, filters=command(
        BotCommands.LogCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command(
        BotCommands.RestartCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command(
        BotCommands.PingCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(bot_help, filters=command(
        BotCommands.HelpCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(stats, filters=command(
        BotCommands.StatsCommand) & CustomFilters.authorized))
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
