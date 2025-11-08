import logging
from threading import Event

from ...context import ctx
from ...dao import Job
from ...dao.enums import JobStatus, JobType, OutputFormat
from ...dao.tier import ENABLED_FORMATS
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(self, job: Job, signal=Event()) -> None:
        self.job = job
        self.signal = signal
        self.user = ctx.users.get(self.job.user_id)

    def process(self):
        logger.info(f'Processing job: {self.job.id}, type: {self.job.type}')
        if self.job.is_done:
            return
        if self.job.done == self.job.total:
            return self.__set_success()
        if self.job.is_running:
            return
        if self.job.type == JobType.FULL_NOVEL_BATCH:
            return self._novel_batch()
        if self.job.type == JobType.NOVEL_BATCH:
            return self._novel_batch()
        if self.job.type == JobType.FULL_NOVEL:
            return self._novel()
        if self.job.type == JobType.NOVEL:
            return self._novel()
        if self.job.type == JobType.VOLUME_BATCH:
            return self._volume_batch()
        if self.job.type == JobType.VOLUME:
            return self._volume()
        if self.job.type == JobType.CHAPTER_BATCH:
            return self._chapter_batch()
        if self.job.type == JobType.CHAPTER:
            return self._chapter()
        if self.job.type == JobType.IMAGE_BATCH:
            return self._image_batch()
        if self.job.type == JobType.IMAGE:
            return self._image()
        if self.job.type == JobType.ARTIFACT_BATCH:
            return self._artifact_batch()
        if self.job.type == JobType.ARTIFACT:
            return self._artifact()
        return self.__set_failed(f'Job type is not supported: {self.job.type}')

    def __set_running(self) -> None:
        ctx.jobs._update(
            self.job.id,
            status=JobStatus.RUNNING,
            started_at=current_timestamp(),
        )

    def __increment(self) -> None:
        ctx.jobs._update(
            self.job.id,
            done=Job.done + 1,
        )
        return True

    def __set_success(self) -> bool:
        # cancel child jobs
        ctx.jobs.cancel(
            self.user,
            self.job.id,
            'Canceled as the parent job is done'
        )
        # update current
        ctx.jobs._update(
            self.job.id,
            status=JobStatus.SUCCESS,
            finished_at=current_timestamp(),
        )
        return True

    def __set_failed(self, reason: str) -> bool:
        # cancel child jobs
        ctx.jobs.cancel(
            self.user,
            self.job.id,
            f'Canceled by parent job. Cause: {reason}'
        )
        # update current
        ctx.jobs._update(
            self.job.id,
            status=JobStatus.FAILED,
            finished_at=current_timestamp(),
        )
        return False

    def _novel_batch(self):
        try:
            urls = self.job.extra.get('urls', [])
            if not urls:
                return self.__set_success()

            self.__set_running()

            full = self.job.type == JobType.FULL_NOVEL_BATCH
            for url in urls:
                ctx.jobs.fetch_novel(self.user, url, full=full, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _novel(self):
        try:
            url = self.job.extra.get('url')
            if not url:
                return self.__set_success()

            self.__set_running()
            novel = ctx.crawler.fetch_novel(url, self.signal)
            ctx.jobs._update(
                self.job.id,
                extra=dict(**self.job.extra, novel_id=novel.id),
            )

            if self.job.type != JobType.FULL_NOVEL:
                return self.__set_success()

            volumes = ctx.volumes.list(novel_id=novel.id)
            if not volumes:
                return self.__set_success()

            for volume in volumes:
                ctx.jobs.fetch_many_volumes(self.user, volume.id, parent_id=self.job.id)

            for format in ENABLED_FORMATS[self.user.tier]:
                ctx.jobs.make_artifact(self.user, novel.id, format, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to fetch novel. {repr(e)}')

    def _volume_batch(self):
        try:
            volume_ids = self.job.extra.get('volume_ids', [])
            if not volume_ids:
                return self.__set_success()

            self.__set_running()
            for volume_id in volume_ids:
                ctx.jobs.fetch_volume(self.user, volume_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _volume(self):
        try:
            volume_id = self.job.extra.get('volume_id')
            if not volume_id:
                return self.__set_success()

            self.__set_running()
            chapters = ctx.chapters.list(volume_id=volume_id, is_crawled=False)
            for chapter in chapters:
                ctx.jobs.fetch_chapter(self.user, chapter.id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _chapter_batch(self):
        try:
            chapter_ids = self.job.extra.get('chapter_ids')
            if not chapter_ids:
                return self.__set_success()

            self.__set_running()
            for chapter_id in chapter_ids:
                ctx.jobs.fetch_chapter(self.user, chapter_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _chapter(self):
        try:
            chapter_id = self.job.extra.get('chapter_id')
            if not chapter_id:
                return self.__set_success()

            self.__set_running()
            chapter = ctx.crawler.fetch_chapter(chapter_id, self.signal)
            if not chapter.is_available:
                return self.__set_failed('Failed to fetch contents')

            images = ctx.chapter_images.list(chapter_id=chapter.id, is_crawled=False)
            if not images:
                return self.__set_success()

            for image in images:
                ctx.jobs.fetch_image(self.user, image.id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to fetch chapter. {repr(e)}')

    def _image_batch(self):
        try:
            image_ids = self.job.extra.get('image_ids')
            if not image_ids:
                return self.__set_success()

            self.__set_running()
            for image_id in image_ids:
                ctx.jobs.fetch_image(self.user, image_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _image(self):
        try:
            image_id = self.job.extra.get('image_id')
            if not image_id:
                return self.__set_success()

            self.__set_running()

            image = ctx.crawler.fetch_image(image_id, self.signal)
            if not image.is_available:
                return self.__set_failed('Failed to download image')

            return self.__set_success()
        except Exception as e:
            self.__set_failed(f'Failed to fetch image. {repr(e)}')

    def _artifact_batch(self):
        try:
            formats = self.job.extra.get('formats')
            novel_id = self.job.extra.get('novel_id')
            if not (novel_id and formats):
                return self.__set_success()

            self.__set_running()
            for fmt in formats:
                ctx.jobs.make_artifact(self.user, novel_id, fmt, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _artifact(self):
        try:
            format = self.job.extra.get('format')
            novel_id = self.job.extra.get('novel_id')
            if not (novel_id and format):
                return self.__set_success()

            if format not in set(OutputFormat):
                return self.__set_failed(f'Invalid format: {format}')

            self.__set_running()

            artifact = ctx.binder.make_artifact(
                novel_id=novel_id,
                format=format,
                job_id=self.job.id,
                user_id=self.user.id,
                signal=self.signal,
            )
            if not artifact.is_available:
                return self.__set_failed('Failed to make artifact')

            return self.__set_success()
        except Exception as e:
            self.__set_failed(f'Failed to make artifact. {repr(e)}')
