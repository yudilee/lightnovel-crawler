import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional, Type

from ...context import ctx
from ...core.crawler import Crawler
from ...core.exeptions import LNException
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_base, extract_host, normalize_url
from . import utils
from .dto import CrawlerIndex

logger = logging.getLogger(__name__)


class SourceLoader:
    def __init__(self) -> None:
        self._store: FTSStore
        self._index: CrawlerIndex
        self._updater: Optional[asyncio.Task[None]] = None
        self.rejected: Dict[str, str] = {}            # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of host/id -> crawler

    def close(self):
        self._store.close()
        self.rejected.clear()
        self.crawlers.clear()
        if self._updater and not self._updater.done():
            self._updater.cancel()

    async def load(self):
        self._store = FTSStore()

        # load offline sources first
        self.load_index(utils.load_offline_source())

        # dynamically import all crawlers
        self.load_crawlers(
            *ctx.config.crawler.local_index_file.parent.glob('**/*.py'),
            *ctx.config.crawler.user_index_file.parent.glob('**/*.py'),
        )

        # run background task get online update
        try:
            if self._updater and not self._updater.done():
                self._updater.cancel()
            self._updater = asyncio.create_task(self.update())
        except asyncio.CancelledError:
            logger.info('Source updater canceled')
        except Exception as e:
            logger.warning(f'Source update failed due to {repr(e)}')

    def load_index(self, index: CrawlerIndex) -> None:
        self._index = index

        # update rejected list
        self.rejected.clear()
        for url, reason in index.rejected.items():
            host = extract_host(url)
            self.rejected[host] = reason

    def load_crawlers(self, *files: Path):
        # only load files that are not cached
        crawlers = (
            (file, crawler)
            for file in files
            for crawler in utils.import_crawlers(file)
        )
        # update cache
        for file, crawler in crawlers:
            sid = getattr(crawler, '__id__')        # crawler id
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
            self._store.insert(normalize(str(file)), sid)
            self._store.insert(normalize(crawler.__name__), sid)
            self._store.insert(' '.join(map(normalize_url, urls)), sid)

    async def update(self, workers=5) -> None:
        assert self._index
        logger.info('Updating sources')
        online_index = await utils.fetch_online_source()
        if online_index.v <= self._index.v:
            logger.info('No latest updates found')
            return

        # save the latest index
        user_file = ctx.config.crawler.user_index_file
        utils.save_source(user_file, self._index)

        # download updated source files
        tasks = []
        lock = asyncio.Semaphore(workers)
        for id, source in online_index.crawlers.items():
            current = self._index.crawlers.get(id)
            if current and current.version >= source.version:
                continue
            user_sources = ctx.config.crawler.user_index_file.parent.parent
            dst_file = (user_sources / source.file_path).resolve()
            task = utils.download(lock, source.url, dst_file)
            self.load_crawlers(dst_file)
            tasks.append(task)
        await asyncio.gather(*tasks)

        # load the online index
        self.load_index(online_index)
        logger.info('Source updated')
        self._updater = None

    def ensure_complete(self):
        if self._updater and not self._updater.done():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.shield(self._updater))

    def create_crawler(self, url: str) -> Crawler:
        if not self._index:
            raise LNException('Sources are not loaded')

        host = extract_host(url)
        if not host:
            raise LNException('Invalid url')

        if host in self.rejected:
            raise LNException(f"{host} is rejected. Reason: {self.rejected[host]}")

        if host not in self.crawlers:
            raise LNException(f"No crawler found for {host}")

        logger.info(f"[{host}] Creating crawler instance")
        home_url = extract_base(url)
        crawler = self.crawlers[host]()

        logger.info(f"[{host}] Initializing crawler")
        crawler.novel_url = url
        crawler.home_url = home_url
        crawler.initialize()
        return crawler
