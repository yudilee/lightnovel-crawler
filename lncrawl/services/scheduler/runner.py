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

    def process(self) -> bool:
        if self.job.is_running:
            child = ctx.jobs._next_pending(self.job.id)
            if not child:
                return self.__set_success()
            JobRunner(child).process()
            self.job = ctx.jobs.get(self.job.id)
            return self.__increment()

        logger.info(f'Processing: {self.job.id}, type: {self.job.type.name}')
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

    def __increment(self) -> bool:
        ctx.jobs._increment(self.job.id)
        self.__send_mail()
        return True

    def __set_success(self) -> bool:
        ctx.jobs._set_done(self.job.id)
        self.__send_mail()
        return True

    def __set_failed(self, reason: str) -> bool:
        ctx.jobs._set_done(self.job.id, reason)
        self.__send_mail()
        return False

    def __send_mail(self):
        if self.job.parent_job_id:
            return
        job = ctx.jobs.get(self.job.id)
        if job.status != JobStatus.SUCCESS:
            return
        if job.type == JobType.FULL_NOVEL:
            ctx.mail.send_full_novel_job_success(self.user, job)

    def _novel_batch(self) -> bool:
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
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _novel(self) -> bool:
        try:
            url = self.job.extra.get('url')
            if not url:
                return self.__set_failed('No novel url')

            self.__set_running()

            novel = ctx.crawler.fetch_novel(url, self.signal)
            extra = dict(**self.job.extra)
            extra['novel_id'] = novel.id
            ctx.jobs._update(
                self.job.id,
                extra=extra,
            )

            if self.job.type != JobType.FULL_NOVEL:
                return self.__set_success()

            volumes = ctx.volumes.list(novel_id=novel.id)
            if not volumes:
                return self.__set_success()

            for volume in volumes:
                ctx.jobs.fetch_volume(self.user, volume.id, parent_id=self.job.id)

            ctx.jobs.make_many_artifacts(
                self.user,
                novel.id,
                *ENABLED_FORMATS[self.user.tier],
                parent_id=self.job.id,
            )

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to fetch novel. {repr(e)}')

    def _volume_batch(self) -> bool:
        try:
            volume_ids = self.job.extra.get('volume_ids', [])
            if not volume_ids:
                return self.__set_success()

            self.__set_running()

            for volume_id in volume_ids:
                ctx.jobs.fetch_volume(self.user, volume_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _volume(self) -> bool:
        try:
            volume_id = self.job.extra.get('volume_id')
            if not volume_id:
                return self.__set_failed('No volume id')

            self.__set_running()

            chapters = ctx.chapters.list(volume_id=volume_id)
            for chapter in chapters:
                ctx.jobs.fetch_chapter(self.user, chapter.id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _chapter_batch(self) -> bool:
        try:
            chapter_ids = self.job.extra.get('chapter_ids')
            if not chapter_ids:
                return self.__set_success()

            self.__set_running()

            for chapter_id in chapter_ids:
                ctx.jobs.fetch_chapter(self.user, chapter_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _chapter(self) -> bool:
        try:
            chapter_id = self.job.extra.get('chapter_id')
            if not chapter_id:
                return self.__set_failed('No chapter id')

            self.__set_running()

            chapter = ctx.crawler.fetch_chapter(chapter_id, self.signal)
            if not chapter.is_available:
                return self.__set_failed('Failed to fetch contents')

            images = ctx.images.list(chapter_id=chapter.id, is_crawled=False)
            if not images:
                return self.__set_success()

            for image in images:
                ctx.jobs.fetch_image(self.user, image.id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to fetch chapter. {repr(e)}')

    def _image_batch(self) -> bool:
        try:
            image_ids = self.job.extra.get('image_ids')
            if not image_ids:
                return self.__set_success()

            self.__set_running()

            for image_id in image_ids:
                ctx.jobs.fetch_image(self.user, image_id, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _image(self) -> bool:
        try:
            image_id = self.job.extra.get('image_id')
            if not image_id:
                return self.__set_failed('No image id')

            self.__set_running()

            image = ctx.crawler.fetch_image(image_id, self.signal)
            if not image.is_available:
                return self.__set_failed('Failed to download image')

            return self.__set_success()
        except Exception as e:
            return self.__set_failed(f'Failed to fetch image. {repr(e)}')

    def _artifact_batch(self) -> bool:
        try:
            novel_id = self.job.extra.get('novel_id')
            if not novel_id:
                return self.__set_failed('No novel id')

            formats = self.job.extra.get('formats')
            if not formats:
                return self.__set_success()

            self.__set_running()

            for fmt in formats:
                ctx.jobs.make_artifact(self.user, novel_id, fmt, parent_id=self.job.id)

            return self.__increment()
        except Exception as e:
            return self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _artifact(self) -> bool:
        try:
            novel_id = self.job.extra.get('novel_id')
            if not novel_id:
                return self.__set_failed('No novel id')

            format = self.job.extra.get('format')
            if not format:
                return self.__set_failed('No output format')

            if format not in set(OutputFormat):
                return self.__set_failed(f'Invalid format: {format}')

            self.__set_running()

            novel_title = self.job.extra.get('novel_title')
            if not novel_title:
                novel_title = ctx.novels.get(novel_id).title

            artifact = ctx.binder.make_artifact(
                format=format,
                novel_id=novel_id,
                novel_title=novel_title,
                job_id=self.job.parent_job_id or self.job.id,
                user_id=self.user.id,
                signal=self.signal,
            )
            if not artifact.is_available:
                return self.__set_failed('Failed to make artifact')

            extra = dict(**self.job.extra)
            extra['artifact_id'] = artifact.id
            extra['novel_title'] = novel_title
            ctx.jobs._update(
                self.job.id,
                extra=extra,
            )

            return self.__set_success()
        except Exception as e:
            return self.__set_failed(f'Failed to make artifact. {repr(e)}')
