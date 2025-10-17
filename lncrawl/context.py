import asyncio
import logging
from functools import cached_property
from typing import Optional

_cache: Optional['AppContext'] = None

logger = logging.getLogger(__name__)


class AppContext:
    def __new__(cls):
        global _cache
        if _cache is None:
            _cache = super().__new__(cls)
        return _cache

    async def prepare(self):
        await asyncio.gather(
            self.db.bootstrap(),
            self.sources.load()
        )

    def cleanup(self):
        global _cache
        _cache = None
        self.db.close()
        self.sources.close()

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
    def sources(self):
        from .services.sources import Sources
        return Sources()

    @cached_property
    def users(self):
        from .server.services.users import UserService
        return UserService()

    @cached_property
    def jobs(self):
        from .server.services.jobs import JobService
        return JobService()

    @cached_property
    def novels(self):
        from .server.services.novels import NovelService
        return NovelService()

    @cached_property
    def artifacts(self):
        from .server.services.artifacts import ArtifactService
        return ArtifactService()

    @cached_property
    def scheduler(self):
        from .server.services.scheduler import JobScheduler
        return JobScheduler()

    @cached_property
    def fetch(self):
        from .server.services.fetch import FetchService
        return FetchService()

    @cached_property
    def metadata(self):
        from .server.services.meta import MetadataService
        return MetadataService()

    @cached_property
    def mail(self):
        from .server.services.mail import MailService
        return MailService()


ctx = AppContext()
