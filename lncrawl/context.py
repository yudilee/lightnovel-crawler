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
            self.sources.prepare()
        )

    def cleanup(self):
        global _cache
        _cache = None
        self.db.close()
        self.sources.cleanup()

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
        from .services.sources.service import Sources
        return Sources()

    @cached_property
    def users(self):
        from .bots.server.services.users import UserService
        return UserService(self)

    @cached_property
    def jobs(self):
        from .bots.server.services.jobs import JobService
        return JobService(self)

    @cached_property
    def novels(self):
        from .bots.server.services.novels import NovelService
        return NovelService(self)

    @cached_property
    def artifacts(self):
        from .bots.server.services.artifacts import ArtifactService
        return ArtifactService(self)

    @cached_property
    def scheduler(self):
        from .bots.server.services.scheduler import JobScheduler
        return JobScheduler(self)

    @cached_property
    def fetch(self):
        from .bots.server.services.fetch import FetchService
        return FetchService(self)

    @cached_property
    def metadata(self):
        from .bots.server.services.meta import MetadataService
        return MetadataService(self)

    @cached_property
    def mail(self):
        from .bots.server.services.mail import MailService
        return MailService(self)


ctx = AppContext()
