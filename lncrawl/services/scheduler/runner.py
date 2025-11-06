import logging
from threading import Event

from ...context import ctx
from ...dao import Job, Artifact
from ...dao.enums import JobStatus, JobType, OutputFormat
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(self, job: Job, signal=Event()) -> None:
        self.job = job
        self.signal = signal
        self.user = ctx.users.get(self.job.user_id)

    def process(self):
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
        if self.job.is_running:
            return
        ctx.jobs._update(
            self.job.id,
            status=JobStatus.RUNNING,
            started_at=current_timestamp(),
        )

    def __set_success(self) -> None:
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

    def __set_failed(self, reason: str) -> None:
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

    def __increment(self) -> None:
        ctx.jobs._update(
            self.job.id,
            done=Job.done + 1,
        )

    def _novel_batch(self):
        try:
            urls = self.job.extra.get('urls', [])
            if not urls:
                return self.__set_success()

            self.__set_running()
            full = self.job.type == JobType.FULL_NOVEL_BATCH
            for url in urls:
                ctx.jobs.fetch_novel(self.user, url, full=full, parent_id=self.job.id)

            self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _novel(self):
        try:
            url = self.job.extra.get('url')
            if not url:
                return self.__set_success()

            self.__set_running()
            novel = ctx.crawler.fetch_novel(url)
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

            self.__increment()
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

            self.__increment()
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

            self.__increment()
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

            self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _chapter(self):
        try:
            chapter_id = self.job.extra.get('chapter_id')
            if not chapter_id:
                return self.__set_success()

            self.__set_running()
            chapter = ctx.crawler.fetch_chapter(chapter_id)
            images = ctx.chapter_images.list(chapter_id=chapter.id, is_crawled=False)
            if not images:
                return self.__set_success()

            for image in images:
                ctx.jobs.fetch_image(self.user, image.id, parent_id=self.job.id)

            self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _image_batch(self):
        try:
            image_ids = self.job.extra.get('image_ids')
            if not image_ids:
                return self.__set_success()

            self.__set_running()
            for image_id in image_ids:
                ctx.jobs.fetch_image(self.user, image_id, parent_id=self.job.id)

            self.__increment()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _image(self):
        try:
            image_id = self.job.extra.get('image_id')
            if not image_id:
                return self.__set_success()

            self.__set_running()
            ctx.crawler.fetch_image(image_id)
            self.__set_success()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')

    def _artifact_batch(self):
        try:
            formats = self.job.extra.get('formats')
            novel_id = self.job.extra.get('novel_id')
            if not (novel_id and formats):
                return self.__set_success()

            self.__set_running()
            for fmt in formats:
                ctx.jobs.make_artifact(self.user, novel_id, fmt, parent_id=self.job.id)

            self.__increment()
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
            with ctx.db.session() as sess:
                artifact = Artifact(
                    novel_id=novel_id,
                    job_id=self.job.id,
                    user_id=self.job.user_id,
                    format=OutputFormat[format],
                )
                sess.add(artifact)
                sess.commit()
            ctx.binder.make_artifact(artifact)
            self.__set_success()
        except Exception as e:
            self.__set_failed(f'Failed to create jobs. {repr(e)}')
