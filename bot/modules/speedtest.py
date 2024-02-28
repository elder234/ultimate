from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from speedtest import Speedtest

from bot import bot, LOGGER
from bot.helper.ext_utils.bot_utils import new_task
from bot.helper.ext_utils.status_utils import get_readable_file_size
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import (
    sendMessage,
    sendPhoto,
    deleteMessage,
    editMessage,
)


@new_task
async def speedtest(_, message):
    msg = await sendMessage(message, "<b>Test Your Download and Upload Speed...</b>")
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    caption = f"""
<pre languange='bash'>
<i>SpeedTest Results</i>
<b>Ping         :</b> <code>{result['ping']} ms</code>
<b>Time        :</b> <code>{result['timestamp']}</code>
<b>Upload       :</b> <code>{get_readable_file_size(result['upload'] / 8)}/s</code>
<b>Download       :</b> <code>{get_readable_file_size(result['download'] / 8)}/s</code>
<b>Sent     :</b> <code>{get_readable_file_size(int(result['bytes_sent']))}</code>
<b>Recieved     :</b> <code>{get_readable_file_size(int(result['bytes_received']))}</code>

<b>Client</b>
<b>IP           :</b> <code>{result['client']['ip']}</code>
<b>Nama         :</b> <code>{result['client']['isp']}</code>
<b>Rating       :</b> <code>{result['client']['isprating']}</code>
<b>Country       :</b> <code>{result['client']['country']}</code>
<b>Latitude     :</b> <code>{result['client']['lat']}</code>
<b>Longitude    :</b> <code>{result['client']['lon']}</code>

<b>Server</b>
<b>Name         :</b> <code>{result['server']['name']}</code>
<b>Sponsor      :</b> <code>{result['server']['sponsor']}</code>
<b>Latency      :</b> <code>{result['server']['latency']}</code>
<b>Country       :</b> <code>{result['server']['country']} ({result['server']['cc']})</code>
<b>Latitude     :</b> <code>{result['server']['lat']}</code>
<b>Longitude    :</b> <code>{result['server']['lon']}</code>
</pre>
"""
    try:
        await sendPhoto(
            message, 
            result["share"], 
            caption
        )
        await deleteMessage(msg)
    except Exception as e:
        LOGGER.error(str(e))
        await editMessage(msg, caption)

bot.add_handler(
    MessageHandler(
        speedtest, 
        filters=command(
            BotCommands.SpeedCommand
        ) & CustomFilters.owner
    )
)