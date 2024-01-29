from requests import get
from time import sleep

from bot import (
    LOGGER,
    BASE_URL,
    BASE_URL_PORT,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
}

try:
    if (
        BASE_URL 
        and BASE_URL_PORT is not None
    ):
        while True:
            try:
                sleep(500)
                get(
                    BASE_URL, 
                    headers=headers, 
                    timeout=5
                )
            except:
                pass

    else:
        LOGGER.warning("Auto Alive is not set up correctly! Don't forget to add HEROKU_APP_NAME or RENDER_APP_NAME to prevent the Apps got shutdown!")

except Exception as e:
    LOGGER.error(e)
