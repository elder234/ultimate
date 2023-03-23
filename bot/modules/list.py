#!/usr/bin/env python3
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex

from bot import LOGGER, bot
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.bot_utils import sync_to_async, new_task


async def list_buttons(user_id, isRecursive=True):
    buttons = ButtonMaker()
    buttons.ibutton("Folders", f"list_types {user_id} folders {isRecursive}")
    buttons.ibutton("Files", f"list_types {user_id} files {isRecursive}")
    buttons.ibutton("Both", f"list_types {user_id} both {isRecursive}")
    buttons.ibutton(f"Recursive: {isRecursive}",
                    f"list_types {user_id} rec {isRecursive}")
    buttons.ibutton("Cancel", f"list_types {user_id} cancel")
    return buttons.build_menu(2)


async def _list_drive(key, message, item_type, isRecursive):
    LOGGER.info(f"listing: {key}")
    gdrive = GoogleDriveHelper()
    msg, button = await sync_to_async(gdrive.drive_list, key, isRecursive=isRecursive, itemType=item_type)
    if button:
        await editMessage(message, msg, button)
    else:
        await editMessage(message, f"Pencarian dengan kata kunci <code>{key}</code> tidak ditemukan")


@new_task
async def select_type(client, query):
    user_id = query.from_user.id
    message = query.message
    key = message.reply_to_message.text.split(maxsplit=1)[1].strip()
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Bukan tugas darimu!", show_alert=True)
    elif data[2] == 'rec':
        await query.answer()
        isRecursive = not bool(eval(data[3]))
        buttons = await list_buttons(user_id, isRecursive)
        return await editMessage(message, 'Pilih tipe yang mau dicari:', buttons)
    elif data[2] == 'cancel':
        await query.answer()
        return await editMessage(message, "Pencarian dibatalkan!")
    await query.answer()
    item_type = data[2]
    isRecursive = eval(data[3])
    await editMessage(message, f"Mencari file dengan kata kunci <code>{key}</code>...")
    await _list_drive(key, message, item_type, isRecursive)


async def drive_list(client, message):
    if len(message.text.split()) == 1:
        return await sendMessage(message, 'Send a search key along with command')
    user_id = message.from_user.id
    buttons = await list_buttons(user_id)
    await sendMessage(message, 'Pilih tipe yang mau dicari:', buttons)

bot.add_handler(MessageHandler(drive_list, filters=command(
    BotCommands.ListCommand) & CustomFilters.authorized))
bot.add_handler(CallbackQueryHandler(
    select_type, filters=regex("^list_types")))
