import logging
import os
import shutil
from threading import Event

from sqlalchemy import delete as sa_delete
from sqlmodel import and_, asc, false, select

from ...context import ctx
from ...dao import Artifact, Job, Novel
from ...dao.enums import JobStatus
from ...utils.file_tools import folder_size, format_size
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


def run_cleaner(signal=Event()) -> None:
    sess = ctx.db.session()
    output_folder = ctx.config.app.output_path
    size_limit = ctx.config.crawler.disk_size_limit
    cutoff = current_timestamp() - 5 * 24 * 3600 * 1000  # 5 days

    logger.info("=== Cleanup begin ===")
    try:
        # Delete canceled jobs
        logger.info('Delete canceled jobs...')
        sess.exec(
            sa_delete(Job)
            .where(Job.status == JobStatus.CANCELED)
            .where(Job.created_at < cutoff)
        )
        sess.commit()
        if signal.is_set():
            return

        # Free up disk space
        if size_limit <= 0:
            return

        current_size = folder_size(output_folder)
        logger.info(f"Current folder size: {format_size(current_size)}")
        if current_size < size_limit:
            return

        # Keep deleting novels to reach target disk size limit
        logger.info('Deleting novels to free up space...')
        for folder in sorted(
            ctx.files.resolve('novels').iterdir(),
            key=lambda p: p.stat().st_mtime,
        ):
            if signal.is_set():
                return
            if not folder.is_dir():
                continue
            try:
                current_size -= folder_size(folder)
                shutil.rmtree(folder, ignore_errors=True)
                with ctx.db.session() as sess:
                    sess.exec(sa_delete(Novel).where(Novel.id == folder.name))
                    sess.commit()
            except Exception:
                logger.debug(f'Could not remove novel: {folder.name}', exc_info=True)
            if current_size < size_limit:
                break

        current_size = folder_size(output_folder)
        logger.info(f"Final folder size: {format_size(current_size)}")

    except Exception:
        logger.error("Cleanup failed", exc_info=True)

    finally:
        sess.close()
        logger.info("=== Cleanup end ===")
