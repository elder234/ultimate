from logging import (
    getLogger,
    FileHandler,
    StreamHandler,
    INFO,
    basicConfig,
    error as log_error,
    warning as log_warning,
)
from os import environ
from requests import get
from time import sleep


basicConfig(
    format="{asctime} - [{levelname[0]}] {name} [{module}:{lineno}] - {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

LOGGER = getLogger("AutoAlive")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
}

try:
    PORT = environ.get("PORT")
    HEROKU_APP_NAME = environ.get("HEROKU_APP_NAME", "")
    RENDER_APP_NAME = environ.get("RENDER_APP_NAME", "")
    if len(HEROKU_APP_NAME) != 0:
        BASE_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com"
        if BASE_URL and PORT is not None:
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
    elif len(RENDER_APP_NAME) != 0:
        BASE_URL = f"https://{RENDER_APP_NAME}.onrender.com"
        if BASE_URL and PORT is not None:
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
        log_warning("Auto Alive is not Set Up correctly! Don't forget to add HEROKU_APP_NAME or RENDER_APP_NAME to prevent the Apps got shutdown!")
except Exception as e:
    log_error(e)
