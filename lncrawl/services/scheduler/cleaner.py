import logging
import shutil
from threading import Event

from ...context import ctx
from ...exceptions import AbortedException
from ...utils.file_tools import folder_size, format_size

logger = logging.getLogger(__name__)


class Cleaner:
    def __init__(self, signal=Event()) -> None:
        self.signal = signal

    @staticmethod
    def run(signal: Event):
        cleaner = Cleaner(signal)
        cleaner.free_disk_size()

    def free_disk_size(self):
        size_limit = ctx.config.crawler.disk_size_limit
        if size_limit <= 0:
            return

        current_size = folder_size(ctx.config.app.output_path)
        logger.info(f"Current folder size: {format_size(current_size)}")
        if current_size < size_limit:
            return

        # Keep deleting novels to reach target disk size limit
        logger.debug('Deleting novels to free up space')
        for folder in sorted(
            ctx.files.resolve('novels').iterdir(),
            key=lambda p: p.stat().st_mtime,
        ):
            if self.signal.is_set():
                raise AbortedException()
            if not folder.is_dir():
                continue
            try:
                size = folder_size(folder)
                current_size -= size
                shutil.rmtree(folder, ignore_errors=True)
                logger.info(f'Deleted novel: {folder.name} [{format_size(size)}]')
                ctx.novels.delete(folder.name)
            except Exception:
                current_size = folder_size(ctx.config.app.output_path)
                logger.info(f'Error removing: {folder.name}', exc_info=True)
            finally:
                if current_size < size_limit:
                    break

        logger.info(f"Current folder size: {format_size(current_size)}")
