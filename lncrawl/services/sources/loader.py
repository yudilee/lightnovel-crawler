import logging
from functools import lru_cache
from pathlib import Path
from threading import Event
from typing import Dict, Type

from ...context import ctx
from ...core.crawler import Crawler
from ...core.taskman import TaskManager
from ...exceptions import ServerErrors
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_base, extract_host, normalize_url
from . import utils
from .dto import CrawlerIndex

logger = logging.getLogger(__name__)


class SourceLoader:
    def __init__(self) -> None:
        self._signal: Event
        self._store: FTSStore
        self._index: CrawlerIndex
        self._taskman: TaskManager
        self.rejected: Dict[str, str] = {}            # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of host/id -> crawler

    def close(self):
        if hasattr(self, '_signal'):
            self._signal.set()
        if hasattr(self, '_store'):
            self._store.close()
        if hasattr(self, '_taskman'):
            self._taskman.close()
        if hasattr(self, '_index'):
            del self._index
        self.rejected.clear()
        self.crawlers.clear()

    def load(self):
        self._signal = Event()
        self._store = FTSStore()
        self._taskman = TaskManager(10)

        # load offline sources first
        self.load_index(utils.load_offline_source())

        # dynamically import all crawlers
        self._taskman.submit_task(
            self.load_crawlers,
            *ctx.config.crawler.local_index_file.parent.glob('**/*.py'),
            *ctx.config.crawler.user_index_file.parent.glob('**/*.py'),
        )

        # run background task get online update
        self._taskman.submit_task(self.update)

    def ensure_load(self):
        self._taskman.as_completed(
            disable_bar=True,
            signal=self._signal,
        )

    def load_index(self, index: CrawlerIndex) -> None:
        self._index = index

        # update rejected list
        self.rejected.clear()
        for url, reason in index.rejected.items():
            host = extract_host(url)
            self.rejected[host] = reason

    def load_crawlers(self, *files: Path):
        futures = [
            self._taskman.submit_task(utils.import_crawlers, file)
            for file in files
        ]
        for crawlers in self._taskman.resolve_as_generator(
            futures,
            disable_bar=True,
            signal=self._signal,
        ):
            for crawler in crawlers:
                if issubclass(crawler, Crawler):
                    yield self.add_crawler(crawler)

    def add_crawler(self, crawler: Type[Crawler]):
        sid = getattr(crawler, '__id__')        # crawler id
        file = getattr(crawler, '__file__')     # file path
        urls = getattr(crawler, 'base_url')     # always a list
        version = getattr(crawler, 'version')   # last edit time

        # add to index if not available
        if sid in self._index.crawlers:
            info = self._index.crawlers[sid]
        else:
            logger.info(f'Found non-indexed crawler: {crawler.__name__}')
            info = utils.create_crawler_info(crawler)
            self._index.crawlers[sid] = info

        # update crawlers list with the latest crawler
        def _set(key: str):
            if key in self.crawlers:
                if version < getattr(self.crawlers[key], 'version'):
                    return  # skip if current crawler is the latest
            self.crawlers[key] = crawler

        _set(sid)
        for url in urls:
            _set(extract_host(url))

        # add keys for searching
        self._store.insert(normalize(file), sid)
        self._store.insert(normalize(crawler.__name__), sid)
        self._store.insert(' '.join(map(normalize_url, urls)), sid)
        return info

    def update(self) -> None:
        assert self._index
        logger.info('Sync online sources')
        online_index = utils.fetch_online_source()
        if online_index.v <= self._index.v:
            logger.info('No latest updates found')
            return

        # save the latest index
        user_file = ctx.config.crawler.user_index_file
        utils.save_source(user_file, self._index)

        # load the online index
        self.load_index(online_index)

        # download updated source files
        futures = []
        for id, source in online_index.crawlers.items():
            current = self._index.crawlers.get(id)
            if current and current.version >= source.version:
                continue
            user_sources = ctx.config.crawler.user_index_file.parent.parent
            dst_file = (user_sources / source.file_path).resolve()
            f = self._taskman.submit_task(ctx.http.download, source.url, dst_file)
            futures.append(f)

        # wait for completion
        for dst_file in self._taskman.resolve_as_generator(
            futures,
            desc='Downloading',
            unit='source',
            signal=self._signal,
        ):
            self.load_crawlers(dst_file)
        logger.info('Source synced.')

    def get_crawler(self, url: str) -> Type[Crawler]:
        self.ensure_load()
        if not self._index:
            raise ServerErrors.source_not_loaded

        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        if host in self.rejected:
            raise ServerErrors.host_rejected.with_detail(self.rejected[host])
        if host not in self.crawlers:
            raise ServerErrors.no_crawler.with_detail(host)

        return self.crawlers[host]

    @lru_cache
    def create_crawler(self, url: str) -> Crawler:
        logger.info(f"Creating crawler instance for {url}")
        crawler = self.get_crawler(url)()
        crawler.home_url = extract_base(url)
        crawler.novel_url = url
        crawler.initialize()
        return crawler
