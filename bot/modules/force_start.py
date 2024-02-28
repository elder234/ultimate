from pyrogram.filters import command
from pyrogram.handlers import MessageHandler

from bot import (
    task_dict,
    bot,
    task_dict_lock,
    OWNER_ID,
    user_data,
    queued_up,
    queued_dl,
    queue_dict_lock,
)
from bot.helper.ext_utils.status_utils import getTaskByGid
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage
from bot.helper.ext_utils.task_manager import start_dl_from_queued, start_up_from_queued


async def remove_from_queue(_, message):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    msg = message.text.split()
    status = msg[1] if len(msg) > 1 and msg[1] in ["fd", "fu"] else ""
    if status and len(msg) > 2 or not status and len(msg) > 1:
        gid = msg[2] if status else msg[1]
        task = await getTaskByGid(gid)
        if task is None:
            await sendMessage(message, f"<b>Task with GID</b> <code>{gid}</code> <b>Not Found !</b>")
            return
    elif reply_to_id := message.reply_to_message_id:
        async with task_dict_lock:
            task = task_dict.get(reply_to_id)
        if task is None:
            await sendMessage(message, "<b>Not Active Duty</b>")
            return
    elif len(msg) in {1, 2}:
        msg = (
            "<b>Respond to a command message when used to start a Task</b>" \
            f" <b>or send</b> <code>/{BotCommands.ForceStartCommand[0]} [GID]</code> <b>atau</b> <code>/{BotCommands.ForceStartCommand[1]} [GID]</code> <b>untuk memulai Tugas secara paksa!</b>" \
            f" <b>You can add</b> <code>fd/fu</code> <b>after the command to forcefully start the Task to Download/Upload!</b>"
        )
        await sendMessage(message, msg)
        return
    if (
        OWNER_ID != user_id
        and task.listener.userId != user_id
        and (user_id not in user_data or not user_data[user_id].get("is_sudo"))
    ):
        await sendMessage(message, "<b>Not Your Duty Buddy !</b>")
        return
    obj = task.task()
    listener = obj.listener
    msg = ""
    async with queue_dict_lock:
        if status == "fu":
            listener.forceUpload = True
            if listener.mid in queued_up:
                await start_up_from_queued(listener.mid)
                msg = "<b>Task successfully started forcefully to Upload!</b>"
        elif status == "fd":
            listener.forceDownload = True
            if listener.mid in queued_dl:
                await start_dl_from_queued(listener.mid)
                msg = "<b>Task successfully started forcefully to Download!</b>"
        else:
            listener.forceDownload = True
            listener.forceUpload = True
            if listener.mid in queued_up:
                await start_up_from_queued(listener.mid)
                msg = "<b>Task successfully started forcefully to Upload!</b>"
            elif listener.mid in queued_dl:
                await start_dl_from_queued(listener.mid)
                msg = "<b>Task successfully started force to Download and will Upload after Download process is complete!</b>"
    if msg:
        await sendMessage(message, msg)

        


bot.add_handler(
    MessageHandler(
        remove_from_queue,
        filters=command(BotCommands.ForceStartCommand) & CustomFilters.authorized,
    )
)