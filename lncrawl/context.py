import logging
import os
from functools import cached_property
from threading import Thread
from typing import List, Optional

_cache: Optional['AppContext'] = None

logger = logging.getLogger(__name__)


class AppContext:
    @cached_property
    def config(self):
        from .config import Config
        return Config()

    @cached_property
    def logger(self):
        from .services.logger import Logger
        return Logger()

    @cached_property
    def db(self):
        from .services.db import DB
        return DB()

    @cached_property
    def mail(self):
        from .services.mail import MailService
        return MailService()

    @cached_property
    def http(self):
        from .services.fetch import FetchService
        return FetchService()

    @cached_property
    def files(self):
        from .services.file import FileService
        return FileService()

    @cached_property
    def sources(self):
        from .services.sources import Sources
        return Sources()

    @cached_property
    def users(self):
        from .services.users import UserService
        return UserService()

    @cached_property
    def novels(self):
        from .services.novels import NovelService
        return NovelService()

    @cached_property
    def tags(self):
        from .services.tags import TagService
        return TagService()

    @cached_property
    def secrets(self):
        from .services.secrets import SecretService
        return SecretService()

    @cached_property
    def volumes(self):
        from .services.volumes import VolumeService
        return VolumeService()

    @cached_property
    def chapters(self):
        from .services.chapters import ChapterService
        return ChapterService()

    @cached_property
    def chapter_images(self):
        from .services.chapter_images import ChapterImageService
        return ChapterImageService()

    @cached_property
    def artifacts(self):
        from .services.artifacts import ArtifactService
        return ArtifactService()

    @cached_property
    def jobs(self):
        from .services.jobs.service import JobService
        return JobService()

    @cached_property
    def history(self):
        from .services.history import ReadHistoryService
        return ReadHistoryService()

    @cached_property
    def crawler(self):
        from .services.crawler import CrawlerService
        return CrawlerService()

    @cached_property
    def binder(self):
        from .services.binder import BinderService
        return BinderService()

    @cached_property
    def scheduler(self):
        from .services.scheduler import JobScheduler
        return JobScheduler()

    def __new__(cls):
        global _cache
        if _cache is None:
            _cache = super().__new__(cls)
        return _cache

    def __init__(self) -> None:
        self.__prepared = False
        self.__threads: List[Thread] = []

    def destroy(self):
        global _cache
        _cache = None
        self.db.close()
        self.mail.close()
        self.sources.close()
        self.scheduler.stop()
        self.__threads.clear()

    def setup(self):
        if self.__prepared:
            return
        self.__prepared = True
        log_level = int(os.getenv('LNCRAWL_LOG_LEVEL', '0'))
        self.logger.setup(log_level)
        self.config.load()
        self.db.bootstrap()
        self.sources.load()
        self.scheduler.start()


ctx: AppContext = AppContext()
