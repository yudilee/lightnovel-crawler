import logging
import shutil
from threading import Event

from sqlalchemy import delete as sa_delete

from ...context import ctx
from ...dao import Job, Novel
from ...dao.enums import JobStatus
from ...utils.file_tools import folder_size, format_size
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


def __delete_canceled() -> None:
    cutoff = current_timestamp() - 5 * 24 * 3600 * 1000  # 5 days
    with ctx.db.session() as sess:
        result = sess.exec(
            sa_delete(Job)
            .where(Job.status == JobStatus.CANCELED)
            .where(Job.created_at < cutoff)
        )
        sess.commit()
        if result.rowcount:
            logger.info(f'Deleted {result.rowcount} canceled jobs')


def __free_disk_size(signal: Event):
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
        if signal.is_set():
            return
        if not folder.is_dir():
            continue

        try:
            size = folder_size(folder)
            current_size -= size
            shutil.rmtree(folder, ignore_errors=True)
            logger.info(f'Deleted novel: {folder.name} [{format_size(size)}]')
            with ctx.db.session() as sess:
                sess.exec(sa_delete(Novel).where(Novel.id == folder.name))
                sess.commit()
        except Exception:
            logger.info(f'Error removing: {folder.name}', exc_info=True)

        if current_size < size_limit:
            break
    logger.info(f"Current folder size: {format_size(current_size)}")


def run_cleaner(signal=Event()) -> None:
    logger.info("=== Cleanup begin ===")
    try:
        __delete_canceled()
        if signal.is_set():
            return

        __free_disk_size(signal)
    except Exception:
        logger.error("Cleanup failed", exc_info=True)

    finally:
        logger.info("=== Cleanup end ===")
