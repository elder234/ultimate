from aiofiles import open as aiopen
from aiofiles.os import path as aiopath, remove
from asyncio import gather, create_subprocess_exec, sleep
from datetime import datetime
from os import execl as osexecl, getpid
from psutil import (
    boot_time, 
    cpu_count, 
    cpu_freq,
    cpu_percent, 
    disk_usage, 
    net_io_counters, 
    Process,
    virtual_memory, 
)
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from pytz import timezone
from signal import signal, SIGINT
from sys import executable
from time import time
from bot import (
    bot,
    bot_name,
    botStartTime,
    config_dict,
    DATABASE_URL,
    INCOMPLETE_TASK_NOTIFIER,
    Intervals,
    IS_PREMIUM_USER,
    LOGGER,
    scheduler,
    user,
    Version,
)
from .helper.ext_utils.bot_utils import cmd_exec, sync_to_async, create_help_buttons
from .helper.ext_utils.db_handler import DbManager
from .helper.ext_utils.files_utils import clean_all, exit_clean_up
from .helper.ext_utils.jdownloader_booter import jdownloader
from .helper.ext_utils.status_utils import get_progress_bar_string, get_readable_file_size, get_readable_time
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.listeners.aria2_listener import start_aria2_listener
from .helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile
from .modules import (
    authorize,
    bot_settings,
    cancel_task,
    clone,
    exec,
    force_start,
    gd_count,
    gd_delete,
    gd_search,
    help,
    mirror_leech,
    rss,
    shell,
    speedtest,
    status,
    torrent_search,
    torrent_select,
    users_settings,
    ytdlp,
)


async def stats(_, message):
    cpu = cpu_freq()
    memory = virtual_memory()
    network = net_io_counters()
    bot_uptime = get_readable_time(time() - botStartTime)
    machine_uptime = get_readable_time(time() - boot_time())
    total, used, free, disk = disk_usage(config_dict['DOWNLOAD_DIR'])
    neofetch, _, _ = await cmd_exec("neofetch --shell_version off --stdout", shell=True)
    
    if await aiopath.exists(".git"):
        commit_time, _, _ = await cmd_exec("git log -1 --pretty=format:'%cr'", shell=True)
        commit_message, _, _ = await cmd_exec("git log -1 --pretty=format:'%s'", shell=True)
    else:
        commit_time = "-"
        commit_message = "-"
    
    DC_ID = {
        1: "US",
        2: "NL",
        3: "US",
        4: "NL",
        5: "SG"
    }
        
    stats = f"""
<pre languange='bash'><code>{neofetch}</code>

<b>CPU</b>
<b>Cores        :</b> <code>{cpu_count(logical=False)}</code>
<b>Logical      :</b> <code>{cpu_count(logical=True)}</code>
<b>Frequency    :</b> <code>{round(cpu.current)}</code>
<code>{get_progress_bar_string(cpu_percent(interval=0.5))} - {cpu_percent(interval=0.5)}%</code>

<b>RAM</b> 
<b>Used     :</b> <code>{get_readable_file_size(memory.used)}</code> [<code>{get_readable_file_size(Process(getpid()).memory_info().rss)}</code>]
<b>Available     :</b> <code>{get_readable_file_size(memory.available)}</code>
<b>Total        :</b> <code>{get_readable_file_size(memory.total)}</code>
<code>{get_progress_bar_string(memory.percent)} - {memory.percent}%</code>

<b>RAM usage</b>
<b>Python       :</b> <code>{get_readable_file_size(Process(getpid()).memory_info().rss)}</code>

<b>Disk</b> 
<b>Used     :</b> <code>{get_readable_file_size(used)}</code>
<b>Available     :</b> <code>{get_readable_file_size(free)}</code>
<b>Total        :</b> <code>{get_readable_file_size(total)}</code>
<code>{get_progress_bar_string(disk)} - {disk}%</code>

<b>Network</b>
<b>Total Download  :</b> <code>{get_readable_file_size(network.bytes_recv)}</code>
<b>Total Upload :</b> <code>{get_readable_file_size(network.bytes_sent)}</code>

<b>Versi</b>
<b>Aria2c       :</b> <code>v{Version.ar}</code>
<b>FFMPEG       :</b> <code>v{Version.ff}</code>
<b>Google       :</b> <code>v{Version.ga}</code>
<b>Java         :</b> <code>v{Version.jv}</code>
<b>MegaSDK      :</b> <code>v{Version.mg}</code>
<b>MyJD         :</b> <code>v{Version.jd}</code>
<b>P7Zip        :</b> <code>v{Version.p7}</code> 
<b>Pyro         :</b> <code>v{Version.pr}</code>
<b>Python       :</b> <code>v{Version.py}</code>
<b>Qbittorrent  :</b> <code>{Version.qb}</code>
<b>Rclone       :</b> <code>{Version.rc}</code>
<b>YT-DLP       :</b> <code>v{Version.yt}</code>

<b>Others</b>
<b>Bot DC       :</b> <code>{bot.me.dc_id} ({DC_ID.get(bot.me.dc_id)})</code>
<b>Bot ID       :</b> <code>{bot.me.id}</code>
<b>Bot Name     :</b> <code>{bot.me.first_name} {(bot.me.last_name or '')}</code>
<b>Bot Username :</b> <code>@{bot_name}</code>
<b>User DC      :</b> <code>{user.me.dc_id if user else '-'} {('(' + DC_ID.get(user.me.dc_id) + ')' if user else '')}</code>
<b>User ID      :</b> <code>{user.me.id if user else '-'}</code>
<b>User Name    :</b> <code>{(user.me.first_name if user else '-')} {((user.me.last_name if user else '') or '')}</code>
<b>User Status  :</b> <code>{'PREMIUM' if IS_PREMIUM_USER else 'FREE'}</code>
<b>Uptime Bot   :</b> <code>{bot_uptime}</code>
<b>Uptime Status :</b> <code>{machine_uptime}</code>
<b>Updated   :</b> <code>{commit_time}</code>
<b>Update    :</b> <code>{commit_message}</code></pre>
"""

    await sendMessage(
        message, 
        stats
    )


async def start(client, message):
    buttons = ButtonMaker()
    buttons.ubutton(
        "Owner", "https://t.me/starkzer")
    buttons.ubutton("Channel", "https://t.me/alpha1anouncementz")
    reply_markup = buttons.build_menu(2)
    if await CustomFilters.authorized(client, message):
        start_string = f"""
<b>Download/Upload from Slow Links to Fast Links!</b>
Send <code>/{BotCommands.HelpCommand[0]}</code> To get available list of commands!

<b>Note :</b>
Always backup Files after Download/Upload Task is completed to avoid Cloud deletion!
"""
    else:
        start_string = """
<b>No permission!</b>

<b>Note :</b>
Join a Group/Channel to use Bots!
If this Group has Topics enabled, Send commands in permitted Topics!
"""

    await sendMessage(
        message, 
        start_string, 
        reply_markup
    )


async def restart(_, message):
    Intervals["stopAll"] = True
    restart_message = await sendMessage(
        message, 
        "<b>Restarting...</b>"
    )
    if scheduler.running:
        scheduler.shutdown(wait=False)
    if qb := Intervals["qb"]:
        qb.cancel()
    if jd := Intervals["jd"]:
        jd.cancel()
    if st := Intervals["status"]:
        for intvl in list(st.values()):
            intvl.cancel()
    await sleep(1)
    await sync_to_async(clean_all)
    await sleep(1)
    proc1 = await create_subprocess_exec("pkill", "-9", "-f", "gunicorn|chrome|firefox|opera|edge|safari")
    proc2 = await create_subprocess_exec("python3", "update.py")
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(
        message, 
        "<b>Test bot response time...</b>"
    )
    end_time = int(round(time() * 1000))
    await editMessage(
        reply, 
        f"🤖 <b>Respon Bot :</b> <code>{end_time - start_time} ms</code>"
    )


async def log(_, message):
    await sendFile(message, "log.txt")


async def bot_help(_, message):
    help_string = f"""
<b>Command Listt</b> <code>@{bot_name}</code>
<code>/{BotCommands.StartCommand}</code> : start bot.
<code>/{BotCommands.HelpCommand[0]}</code> or <code>/{BotCommands.HelpCommand[1]}</code> : Check all Bot  Commands
<code>/{BotCommands.MirrorCommand[0]}</code> or <code>/{BotCommands.MirrorCommand[1]}</code> : Start mirroring to Google Drive.
<code>/{BotCommands.QbMirrorCommand[0]}</code> or <code>/{BotCommands.QbMirrorCommand[1]}</code> : Start Mirroring to Google Drive using qBittorrent.
<code>/{BotCommands.JdMirrorCommand[0]}</code> or <code>/{BotCommands.JdMirrorCommand[1]}</code> : Start Mirroring to Google Drive using  JDownloader.
<code>/{BotCommands.YtdlCommand[0]}</code> or <code>/{BotCommands.YtdlCommand[1]}</code> : Start Mirroring to Google Drive using YT-DLP.
<code>/{BotCommands.LeechCommand[0]}</code> or <code>/{BotCommands.LeechCommand[1]}</code> : Leech to Telegram using Aria2.
<code>/{BotCommands.QbLeechCommand[0]}</code> or <code>/{BotCommands.QbLeechCommand[1]}</code> : Leech to Telegram using qBittorrent.
<code>/{BotCommands.JdLeechCommand[0]}</code> or <code>/{BotCommands.JdLeechCommand[1]}</code> : Leech to Telegram using JDownloader.
<code>/{BotCommands.YtdlLeechCommand[0]}</code> or <code>/{BotCommands.YtdlLeechCommand[1]}</code> : Leech to Telegram using YT-DLP.
<code>/{BotCommands.CloneCommand[0]}</code> or <code>/{BotCommands.CloneCommand[1]}</code> [gdriveUrl] : Duplicate files/folders Google Drive.
<code>/{BotCommands.CountCommand[0]}</code> or <code>/{BotCommands.CountCommand[1]}</code> [gdriveUrl] : Count file/folder of Google Google Drive.
<code>/{BotCommands.DeleteCommand[0]}</code> or <code>/{BotCommands.DeleteCommand[1]}</code> [gdriveUrl] : Delete file/folder Google Drive (Only Owner & Sudo).
<code>/{BotCommands.UserSetCommand[0]}</code> or <code>/{BotCommands.UserSetCommand[1]}</code> : User Settings.
<code>/{BotCommands.BotSetCommand[0]}</code> or <code>/{BotCommands.BotSetCommand[1]}</code> : Arangement Bot (Only Owner & Sudo).
<code>/{BotCommands.BtSelectCommand[0]}</code> or <code>/{BotCommands.BtSelectCommand[1]}</code> : Select files from Torrents.
<code>/{BotCommands.CancelTaskCommand[0]}</code> or <code>/{BotCommands.CancelTaskCommand[1]}</code> [GID] : Cancel Task.
<code>/{BotCommands.ForceStartCommand[0]}</code> or <code>/{BotCommands.ForceStartCommand[1]}</code> [GID] : Force start Task.
<code>/{BotCommands.CancelAllCommand[0]}</code> or <code>/{BotCommands.CancelAllCommand[1]}</code> : Cancel All Task (Only Owner & Sudo).
<code>/{BotCommands.ListCommand[0]}</code> or <code>/{BotCommands.ListCommand[1]}</code> [query] : Search for files/foldeer in Google Drive
<code>/{BotCommands.SearchCommand[0]}</code> or <code>/{BotCommands.SearchCommand[1]}</code> [query] : Searching for Torrents Using The API.
<code>/{BotCommands.StatusCommand[0]}</code> or <code>/{BotCommands.StatusCommand[1]}</code> : Shows a status of all the downloads.
<code>/{BotCommands.StatsCommand[0]}</code> or <code>/{BotCommands.StatsCommand[1]}</code> : Show stats of the machine where the bot is hosted in.
<code>/{BotCommands.PingCommand[0]}</code> or <code>/{BotCommands.PingCommand[1]}</code> : Check how long it takes to Ping the Bot.
<code>/{BotCommands.SpeedCommand[0]}</code> or <code>/{BotCommands.SpeedCommand[1]}</code> : Testing Bot connection speed (Only Owner & Sudo).
<code>/{BotCommands.AuthorizeCommand[0]}</code> or <code>/{BotCommands.AuthorizeCommand[1]}</code> : Authorize a chat or a user to use the bot (Only Owner & Sudo).
<code>/{BotCommands.UnAuthorizeCommand[0]}</code> or <code>/{BotCommands.UnAuthorizeCommand[1]}</code> : Unauthorize a chat or a user to use the bot (Only Owner & Sudo).
<code>/{BotCommands.UsersCommand[0]}</code> or <code>/{BotCommands.UsersCommand[1]}</code> : show users settings (Only Owner & Sudo).
<code>/{BotCommands.AddSudoCommand[0]}</code> or <code>/{BotCommands.AddSudoCommand[1]}</code> : Add sudo User (Only Owner).
<code>/{BotCommands.RmSudoCommand[0]}</code> or <code>/{BotCommands.RmSudoCommand[1]}</code> : Remove Suso User (Only Owner).
<code>/{BotCommands.RestartCommand[0]}</code> or <code>/{BotCommands.RestartCommand[1]}</code> : Restart and update the bot (Only Owner & Sudo).
<code>/{BotCommands.LogCommand[0]}</code> or <code>/{BotCommands.LogCommand[1]}</code> : Get a log file of the bot. Handy for getting crash reports (Only Owner & Sudo).
<code>/{BotCommands.ShellCommand[0]}</code> or <code>/{BotCommands.ShellCommand[1]}</code> : Run shell commands (Only Owner).
<code>/{BotCommands.ExecCommand[0]}</code> or <code>/{BotCommands.ExecCommand[1]}</code> : Exec async functions  (Only Owner).
<code>/{BotCommands.AExecCommand[0]}</code> or <code>/{BotCommands.AExecCommand[1]}</code> : Executes Async Exec Function (Only Owner).
<code>/{BotCommands.ClearLocalsCommand[0]}</code> or <code>/{BotCommands.ClearLocalsCommand[1]}</code> : Remove local Sync Exec or Async Exec (Only Owner)
<code>/{BotCommands.RssCommand}</code> : Menu RSS.

<b>NOTE :</b> Send a command without arguments to see the command in detail!
"""
    await sendMessage(
        message, 
        help_string
    )


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0
    
    # Get thread_id from AUTHORIZED_CHATS
    if chat_id == 0:
        chat_id = None
        thread_id = None
        if authorized_chat_id := config_dict.get("AUTHORIZED_CHATS"):
            if not isinstance(authorized_chat_id, int):
                if ":" in authorized_chat_id:
                    chat_id = authorized_chat_id.split(":")[0]
                    thread_id = authorized_chat_id.split(":")[1]

            if (
                chat_id is not None
                and not isinstance(chat_id, int)
                and chat_id.isdigit()
            ):
                chat_id = int(chat_id)

            if (
                thread_id is not None
                and not isinstance(thread_id, int)
                and thread_id.isdigit()
            ):
                thread_id = int(thread_id)

    async def send_incompelete_task_message(cid, msg):
        try:
            if msg.startswith('<b>Bot Restarted Successfully!</b>'):
                await bot.edit_message_text(
                    chat_id=chat_id, 
                    message_id=msg_id, 
                    text=msg
                )
                await remove(".restartmsg")
            else:
                await bot.send_message(
                    chat_id=cid, 
                    text=msg, 
                    disable_web_page_preview=True,
                    disable_notification=True,
                    message_thread_id=thread_id,
                )
        except Exception as e:
            LOGGER.error(e)

    now = datetime.now(timezone(f"Africa/Accra"))
    if INCOMPLETE_TASK_NOTIFIER and DATABASE_URL:
        if notifier_dict := await DbManager().get_incomplete_tasks():
            for cid, data in notifier_dict.items():
                msg = f"""
{'<b>Bot restarted Successfully🎇</b>' if cid == chat_id else '<b>Bot Restarted !🎇</b>'}
<pre languange="bash"><b>Day     :</b> <code>{now.strftime('%A')}</code>
<b>Date   :</b> <code>{now.strftime('%d %B %Y')}</code>
<b>Time     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>
</pre>           
"""
                if data.items():
                    msg += f"<b>Unfinished Tasks:</b>"
                for tag, links in data.items():
                    msg += f"\n{tag} :"
                    for index, link in enumerate(links, start=1):
                        msg += f"\n <a href='{link}'>Task {index}</a>"
                        if len(msg.encode()) > 4000:
                            await send_incompelete_task_message(cid, msg)
                            msg = ''
                if msg:
                    await send_incompelete_task_message(cid, msg)

    if await aiopath.isfile(".restartmsg"):
        try:
            msg = f"""
<b>Bot Restarted Successfully 🎇!</b>
<pre languange="bash"><b>Day     :</b> <code>{now.strftime('%A')}</code>
<b>Date   :</b> <code>{now.strftime('%d %B %Y')}</code>
<b>Time     :</b> <code>{now.strftime('%H:%M:%S WIB')}</code>
</pre>           
"""
            await bot.edit_message_text(
                chat_id=chat_id, 
                message_id=msg_id, 
                text=msg
            )
        except:
            pass
        await remove(".restartmsg")


async def main():
    jdownloader.initiate()
    await gather(
        sync_to_async(clean_all),
        torrent_search.initiate_search_tools(), 
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
        sync_to_async(start_aria2_listener, wait=False),
    )
    create_help_buttons()
    
    bot.add_handler(
        MessageHandler(
            start, 
            filters=command(
                BotCommands.StartCommand
            )
        )
    )
    bot.add_handler(
        MessageHandler(
            log, 
            filters=command(
                BotCommands.LogCommand
            ) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            restart, 
            filters=command(
                BotCommands.RestartCommand
            ) & CustomFilters.sudo
        )
    )
    bot.add_handler(
        MessageHandler(
            ping, 
            filters=command(
                BotCommands.PingCommand
            ) & CustomFilters.authorized
        )
    )
    bot.add_handler(
        MessageHandler(
            bot_help, 
            filters=command(
                BotCommands.HelpCommand
            ) & CustomFilters.authorized
        )
    )
    bot.add_handler(
        MessageHandler(
            stats, 
            filters=command(
                BotCommands.StatsCommand
            ) & CustomFilters.authorized
        )
    )
    LOGGER.info(f"Bot Started! -> @{bot_name}")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
