import logging
from threading import Event
from typing import Any, Optional, Set

from ...context import ctx
from ...dao import Job
from ...dao.enums import JobStatus, JobType, OutputFormat
from ...dao.tier import ENABLED_FORMATS
from ...exceptions import AbortedException, ServerError
from ...utils.event_lock import EventLock
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)

__lock = EventLock()
__queue: Set[str] = set()


def run_pending(signal: Event):
    with __lock.using(signal):
        job = ctx.jobs._pending(__queue)
        if not job:
            return
        __queue.add(job.id)

    try:
        JobRunner(job, signal).process()
    finally:
        with __lock.using(signal):
            __queue.remove(job.id)


class JobRunner:
    def __init__(self, job: Job, signal=Event()) -> None:
        self.job = job
        self.signal = signal
        self.user = ctx.users.get(self.job.user_id)

    def process(self) -> bool:
        logger.info(f'Processing [b]{self.job.type.name}[/b]: {self.job.id}')
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
        return self.__set_done(f'Job type is not supported: [b]{self.job.type}[/b]')

    # ------------------------------------------------------------------ #
    #                               Helpers                              #
    # ------------------------------------------------------------------ #

    def __refresh(self):
        with ctx.db.session() as sess:
            self.job = sess.get_one(Job, self.job.id)

    def __set_running(self) -> None:
        with ctx.db.session() as sess:
            now = current_timestamp()
            ctx.jobs._update(
                sess,
                self.job.id,
                started_at=now,
                status=JobStatus.RUNNING,
            )
            sess.commit()
            self.job.started_at = now
            self.job.status = JobStatus.RUNNING
        self.__send_mail()

    def __increment(self) -> bool:
        with ctx.db.session() as sess:
            ctx.jobs._increment_up(sess, self.job.id)
            sess.commit()
        self.__refresh()
        self.__send_mail()
        return True

    def __set_done(
        self,
        error: str = '',
        err_source: Optional[Exception] = None
    ) -> bool:
        if error and err_source:
            error = (
                ServerError(500, error)
                .with_traceback(err_source.__traceback__)
                .format(True)
            )
        with ctx.db.session() as sess:
            if error:
                ctx.jobs._fail(sess, self.job.id, error.strip())
            else:
                ctx.jobs._success(sess, self.job.id)
            sess.commit()
        self.__refresh()
        self.__send_mail()
        return not error

    def __set_extra(self, **values: Any) -> None:
        extra = dict(**self.job.extra)
        for k, v in values.items():
            extra[k] = v
        with ctx.db.session() as sess:
            ctx.jobs._update(
                sess,
                self.job.id,
                extra=extra,
            )
            sess.commit()
            self.job.extra = extra

    def __send_mail(self):
        if self.job.parent_job_id:
            return
        if self.job.status != JobStatus.SUCCESS:
            return
        if self.job.type == JobType.FULL_NOVEL:
            ctx.mail.send_full_novel_job_success(self.user, self.job)

    # ------------------------------------------------------------------ #
    #                             Job Runners                            #
    # ------------------------------------------------------------------ #

    def _novel_batch(self) -> bool:
        try:
            urls = self.job.extra.get('urls')
            if not urls:
                return self.__set_done()

            urls = set(urls)
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                urls -= set([job.extra.get('url') for job in jobs])
            else:
                self.__set_running()

            full = self.job.type == JobType.FULL_NOVEL_BATCH
            for url in sorted(urls):
                ctx.jobs.fetch_novel(
                    self.user,
                    url,
                    full=full,
                    parent_id=self.job.id
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _novel(self) -> bool:
        try:
            url = self.job.extra.get('url')
            if not url:
                return self.__set_done('No novel url')

            added_types = {}
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                added_types = {job.type: job.id for job in jobs}
            else:
                self.__set_running()

            novel = ctx.crawler.fetch_novel(
                self.user.id,
                url,
                self.signal,
            )
            self.__set_extra(novel_id=novel.id)

            if self.job.type != JobType.FULL_NOVEL:
                return self.__set_done()

            if JobType.VOLUME_BATCH not in added_types:
                volumes = ctx.volumes.list(novel_id=novel.id)
                if not volumes:
                    return self.__set_done()

                job = ctx.jobs.fetch_many_volumes(
                    self.user,
                    *(volume.id for volume in volumes),
                    parent_id=self.job.id,
                    novel_id=novel.id,
                    novel_title=novel.title,
                )
                added_types[job.type] = job.id

            if JobType.ARTIFACT_BATCH not in added_types:
                ctx.jobs.make_many_artifacts(
                    self.user,
                    novel.id,
                    *ENABLED_FORMATS[self.user.tier],
                    parent_id=self.job.id,
                    novel_title=novel.title,
                    depends_on=added_types[JobType.VOLUME_BATCH],
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done('Failed to fetch novel', e)

    def _volume_batch(self) -> bool:
        try:
            volume_ids = self.job.extra.get('volume_ids')
            if not volume_ids:
                return self.__set_done()

            volume_ids = set(volume_ids)
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                volume_ids -= set([job.extra.get('volume_id') for job in jobs])
            else:
                self.__set_running()

            for volume_id in volume_ids:
                ctx.jobs.fetch_volume(
                    self.user,
                    volume_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get('novel_title'),
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _volume(self) -> bool:
        try:
            volume_id = self.job.extra.get('volume_id')
            if not volume_id:
                return self.__set_done('No volume id')

            chapter_ids = set([
                chapter.id
                for chapter in ctx.chapters.list(volume_id=volume_id)
            ])

            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                chapter_ids -= set([job.extra.get('chapter_id') for job in jobs])
            else:
                self.__set_running()

            for chapter_id in chapter_ids:
                ctx.jobs.fetch_chapter(
                    self.user,
                    chapter_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get('novel_title'),
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _chapter_batch(self) -> bool:
        try:
            chapter_ids = self.job.extra.get('chapter_ids')
            if not chapter_ids:
                return self.__set_done()

            chapter_ids = set(chapter_ids)
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                chapter_ids -= set([job.extra.get('chapter_id') for job in jobs])
            else:
                self.__set_running()

            for chapter_id in chapter_ids:
                ctx.jobs.fetch_chapter(
                    self.user,
                    chapter_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get('novel_title'),
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _chapter(self) -> bool:
        try:
            chapter_id = self.job.extra.get('chapter_id')
            if not chapter_id:
                return self.__set_done('No chapter id')

            added_types = {}
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                added_types = {job.type: job.id for job in jobs}
            else:
                self.__set_running()

            chapter = ctx.crawler.fetch_chapter(
                self.user.id,
                chapter_id,
                self.signal,
            )
            if not chapter.is_available:
                return self.__set_done('Failed to fetch contents')

            if JobType.IMAGE_BATCH not in added_types:
                images = ctx.images.list(chapter_id=chapter.id, is_crawled=False)
                if not images:
                    return self.__set_done()

                ctx.jobs.fetch_many_images(
                    self.user,
                    *(image.id for image in images),
                    parent_id=self.job.id,
                    chapter_id=chapter.id,
                    chapter_title=chapter.title,
                    novel_id=chapter.novel_id,
                    novel_title=self.job.extra.get('novel_title'),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done('Failed to fetch chapter', e)

    def _image_batch(self) -> bool:
        try:
            image_ids = self.job.extra.get('image_ids')
            if not image_ids:
                return self.__set_done()

            image_ids = set(image_ids)
            if self.job.is_running:
                jobs = ctx.jobs.get_children(self.job.id)
                image_ids -= set([job.extra.get('image_id') for job in jobs])
            else:
                self.__set_running()

            for image_id in image_ids:
                ctx.jobs.fetch_image(
                    self.user,
                    image_id,
                    parent_id=self.job.id,
                    novel_id=self.job.extra.get('novel_id'),
                    novel_title=self.job.extra.get('novel_title'),
                    chapter_id=self.job.extra.get('chapter_id'),
                    chapter_title=self.job.extra.get('chapter_title'),
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _image(self) -> bool:
        try:
            image_id = self.job.extra.get('image_id')
            if not image_id:
                return self.__set_done('No image id')

            if not self.job.is_running:
                self.__set_running()

            image = ctx.crawler.fetch_image(
                self.user.id,
                image_id,
                self.signal,
            )
            if not image.is_available:
                return self.__set_done('Failed to download image')

            return self.__set_done()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done('Failed to fetch image', e)

    def _artifact_batch(self) -> bool:
        try:
            novel_id = self.job.extra.get('novel_id')
            if not novel_id:
                return self.__set_done('No novel id')

            formats = self.job.extra.get('formats')
            if not formats:
                return self.__set_done()

            format_job_map = {}
            if self.job.is_running:
                for job in ctx.jobs.get_children(self.job.id):
                    format = job.extra['format']
                    format_job_map[OutputFormat(format)] = job.id
            else:
                self.__set_running()

            added_format = set(format_job_map.keys())
            formats = set(map(OutputFormat, formats))
            need_epub = formats & ctx.binder.depends_on_epub
            if need_epub:
                formats.add(OutputFormat.epub)
            if not formats:
                return self.__set_done()

            for format in sorted(formats - need_epub - added_format):
                job = ctx.jobs.make_artifact(
                    self.user,
                    novel_id,
                    format,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get('novel_title'),
                )
                format_job_map[format] = job.id

            epub_job_id = format_job_map[OutputFormat.epub]
            if not epub_job_id:
                return self.__set_done('Failed to create epub request')

            for format in sorted(need_epub - added_format):
                job = ctx.jobs.make_artifact(
                    self.user,
                    novel_id,
                    format,
                    parent_id=self.job.id,
                    depends_on=epub_job_id,
                )

            return self.__increment()
        except Exception as e:
            return self.__set_done('Failed to create requests', e)

    def _artifact(self) -> bool:
        try:
            novel_id = self.job.extra.get('novel_id')
            if not novel_id:
                return self.__set_done('No novel id')

            format = self.job.extra.get('format')
            if not format:
                return self.__set_done('No output format')

            if format not in set(OutputFormat):
                return self.__set_done('Invalid format: {format}')

            if not self.job.is_running:
                self.__set_running()

            novel_title = self.job.extra.get('novel_title')
            if not novel_title:
                novel_title = ctx.novels.get(novel_id).title

            artifact = ctx.binder.make_artifact(
                format=format,
                novel_id=novel_id,
                novel_title=novel_title,
                depends_on=self.job.depends_on,
                job_id=self.job.id,
                user_id=self.user.id,
                signal=self.signal,
            )
            if not artifact.is_available:
                return self.__set_done('Failed to make artifact')

            self.__set_extra(
                artifact_id=artifact.id,
                novel_title=novel_title
            )
            return self.__set_done()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done('Failed to make artifact', e)
