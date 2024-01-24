from aiofiles.os import listdir
from json import dump
from random import randint

from bot import config_dict, LOGGER, jd_lock
from bot.helper.ext_utils.bot_utils import (
    cmd_exec,
    new_task,
    sync_to_async,
)
from myjd import Myjdapi
from myjd.exception import (
    MYJDException,
    MYJDAuthFailedException,
    MYJDEmailForbiddenException,
    MYJDEmailInvalidException,
    MYJDErrorEmailNotConfirmedException,
)


class JDownloader(Myjdapi):
    def __init__(self):
        super().__init__()
        self._username = ""
        self._password = ""
        self._device_name = ""
        self.error = "JDownloader Credentials tidak ditemukan!"
        self.device = None
        self.set_app_key("mltb")

    @new_task
    async def initiate(self):
        self.device = None
        async with jd_lock:
            is_connected = await sync_to_async(self.jdconnect)
            if is_connected:
                self.boot()
                await sync_to_async(self.connectToDevice)

    @new_task
    async def boot(self):
        await cmd_exec(["pkill", "-9", "-f", "safari"])
        self.device = None
        self.error = "Menghubungkan ke JDownloader...\nCoba lagi setelah beberapa detik!"
        self._device_name = f"{randint(0, 1000)}"
        logs = await listdir("/JDownloader/logs")
        if len(logs) > 2:
            LOGGER.info("Starting JDownloader... This might take up to 5 sec")
        else:
            LOGGER.info(
                "Starting JDownloader... This might take up to 15 sec and might restart once after build!"
            )
        jdata = {
            "autoconnectenabledv2": True,
            "password": config_dict["JD_PASS"],
            "devicename": f"{self._device_name}",
            "email": config_dict["JD_EMAIL"],
        }
        with open(
            "/JDownloader/cfg/org.jdownloader.api.myjdownloader.MyJDownloaderSettings.json",
            "w",
        ) as sf:
            sf.truncate(0)
            dump(jdata, sf)
        cmd = "safari -Dsun.jnu.encoding=UTF-8 -Dfile.encoding=UTF-8 -Djava.awt.headless=true -jar /JDownloader/JDownloader.jar"
        _, _, code = await cmd_exec(cmd, shell=True)
        if code != 0:
            self.boot()

    def jdconnect(self):
        if not config_dict["JD_EMAIL"] or not config_dict["JD_PASS"]:
            return False
        try:
            self.connect(config_dict["JD_EMAIL"], config_dict["JD_PASS"])
            LOGGER.info("JDownloader is connected!")
            return True
        except (
            MYJDAuthFailedException,
            MYJDEmailForbiddenException,
            MYJDEmailInvalidException,
            MYJDErrorEmailNotConfirmedException,
        ) as err:
            self.error = f"{err}".strip()
            LOGGER.info(f"Failed to connect with JDownloader! ERROR: {self.error}")
            self.device = None
            return False
        except MYJDException as e:
            self.error = f"{e}".strip()
            LOGGER.info(
                f"Failed to connect with JDownloader! Retrying... ERROR: {self.error}"
            )
            return self.jdconnect()

    def connectToDevice(self):
        self.error = "Menghubungkan ke Device..."
        while True:
            self.device = None
            if not config_dict["JD_EMAIL"] or not config_dict["JD_PASS"]:
                return
            try:
                self.update_devices()
                if not (devices := self.list_devices()):
                    continue
                for device in devices:
                    if self._device_name == device["name"]:
                        self.device = self.get_device(f"{self._device_name}")
                        break
                else:
                    continue
            except:
                continue
            break
        self.device.enable_direct_connection()
        self.error = ""
        LOGGER.info("JDownloader Device have been Connected!")


jdownloader = JDownloader()