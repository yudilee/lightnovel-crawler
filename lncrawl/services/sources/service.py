import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Type

from ...context import ctx
from ...core.crawler import Crawler
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_host, normalize_url
from . import utils
from .dto import CrawlerIndex, SourceItem

logger = logging.getLogger(__name__)


class Sources:
    def __init__(self) -> None:
        self._store: FTSStore
        self._index: CrawlerIndex
        self._updater: Optional[asyncio.Task[None]] = None
        self.rejected: Dict[str, str] = {}            # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of host/id -> crawler

    def cleanup(self):
        self._store.close()
        self.rejected.clear()
        self.crawlers.clear()
        if self._updater and not self._updater.done():
            self._updater.cancel()

    async def prepare(self):
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

    def list(
        self,
        query: Optional[str] = None,
        *,
        include_rejected: bool = False,
        can_search: Optional[bool] = None,
        can_login: Optional[bool] = None,
        can_logout: Optional[bool] = None,
        has_mtl: Optional[bool] = None,
        has_manga: Optional[bool] = None,
    ) -> List[Tuple[str, SourceItem]]:
        if not self._index:
            return []

        if query:
            ids = self._store.search(normalize(query))
            infos = [self._index.crawlers[id] for id in ids]
        else:
            infos = list(self._index.crawlers.values())

        result: List[Tuple[str, SourceItem]] = []
        for info in infos:
            crawler = self.crawlers.get(info.id)
            if not crawler:
                continue
            if can_search is not None and info.can_search != can_search:
                continue
            if can_login is not None and info.can_login != can_login:
                continue
            if can_logout is not None and info.can_logout != can_logout:
                continue
            if has_mtl is not None and info.has_mtl != has_mtl:
                continue
            if has_manga is not None and info.has_manga != has_manga:
                continue
            for url in info.base_urls:
                if not include_rejected and extract_host(url) in self.rejected:
                    continue
                item = SourceItem(info=info, crawler=crawler)
                result.append((url, item))
        return result

    def get(self, query: str) -> Optional[SourceItem]:
        if query not in self._index.crawlers:
            ids = self._store.search(normalize(query))
            if len(ids) != 1:
                raise Exception(f'{len(ids)} crawlers found by the query')
            query = ids[0]
        info = self._index.crawlers[query]
        return SourceItem(
            info=info,
            crawler=self.crawlers[info.id],
        )
