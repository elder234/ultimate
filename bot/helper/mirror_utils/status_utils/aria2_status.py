from time import time

from bot import aria2, LOGGER
from bot.helper.ext_utils.bot_utils import sync_to_async
from bot.helper.ext_utils.status_utils import MirrorStatus, get_readable_time


def get_download(gid, old_info=None):
    try:
        res = aria2.get_download(gid)
        return res or old_info
    except Exception as e:
        LOGGER.error(f"{e}: Aria2c, Error while getting torrent info")
        return old_info


class Aria2Status:
    def __init__(self, listener, gid, seeding=False, queued=False):
        self.listener = listener
        self.queued = queued
        self.seeding = seeding
        self.start_time = 0
        self._download = None
        self._gid = gid

    def update(self):
        if self._download is None:
            self._download = get_download(self._gid, self._download)
        else:
            self._download = self._download.live
        if self._download.followed_by_ids:
            self._gid = self._download.followed_by_ids[0]
            self._download = get_download(self._gid)

    def progress(self):
        return self._download.progress_string()

    def processed_bytes(self):
        return self._download.completed_length_string()

    def speed(self):
        return self._download.download_speed_string()

    def name(self):
        return self._download.name

    def size(self):
        return self._download.total_length_string()

    def eta(self):
        return self._download.eta_string()

    async def status(self):
        await sync_to_async(self.update)
        if self._download.is_waiting or self.queued:
            if self.seeding:
                return MirrorStatus.STATUS_QUEUEUP
            else:
                return MirrorStatus.STATUS_QUEUEDL
        elif self._download.is_paused:
            return MirrorStatus.STATUS_PAUSED
        elif self._download.seeder and self.seeding:
            return MirrorStatus.STATUS_SEEDING
        else:
            return MirrorStatus.STATUS_DOWNLOADING

    def seeders_num(self):
        return self._download.num_seeders

    def leechers_num(self):
        return self._download.connections

    def uploaded_bytes(self):
        return self._download.upload_length_string()

    def seed_speed(self):
        return self._download.upload_speed_string()

    def ratio(self):
        return f"{round(self._download.upload_length / self._download.completed_length, 3)}"

    def seeding_time(self):
        return get_readable_time(time() - self.start_time)

    def task(self):
        return self

    def gid(self):
        return self._gid

    async def cancel_task(self):
        self.listener.isCancelled = True
        await sync_to_async(self.update)
        if self._download.seeder and self.seeding:
            LOGGER.info(f"Cancelling Seed: {self.name()}")
            await self.listener.onUploadError(
                f"Seeding dihentikan!\nRatio : {self.ratio()} | Waktu : {self.seeding_time()}"
            )
            await sync_to_async(aria2.remove, [self._download], force=True, files=True)
        elif downloads := self._download.followed_by:
            LOGGER.info(f"Cancelling Download: {self.name()}")
            await self.listener.onDownloadError("Unduhan dibatalkan oleh User!")
            downloads.append(self._download)
            await sync_to_async(aria2.remove, downloads, force=True, files=True)
        else:
            if self.queued:
                LOGGER.info(f"Cancelling QueueDl: {self.name()}")
                msg = "Tugas ini dihapus dari antrian!"
            else:
                LOGGER.info(f"Cancelling Download: {self.name()}")
                msg = "Unduhan dibatalkan oleh User!"
            await self.listener.onDownloadError(msg)
            await sync_to_async(aria2.remove, [self._download], force=True, files=True)
