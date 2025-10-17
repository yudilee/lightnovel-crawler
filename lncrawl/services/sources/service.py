import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Type

from ...core.crawler import Crawler
from ...core.exeptions import LNException
from ...utils.fts_store import FTSStore
from ...utils.text_tools import normalize
from ...utils.url_tools import extract_host
from .dto import CrawlerIndex, SourceItem
from .loader import SourceLoader

logger = logging.getLogger(__name__)


class Sources(SourceLoader):
    def __init__(self) -> None:
        self._store: FTSStore
        self._index: CrawlerIndex
        self._updater: Optional[asyncio.Task[None]] = None
        self.rejected: Dict[str, str] = {}            # Map of host -> rejection reason
        self.crawlers: Dict[str, Type[Crawler]] = {}  # Map of host/id -> crawler

    @property
    def version(self) -> int:
        return self._index.v

    def is_rejected(self, url: str) -> Optional[str]:
        host = extract_host(url)
        return self.rejected.get(host)

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
            raise LNException('Sources are not loaded')

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
        if query in self._index.crawlers:
            info = self._index.crawlers[query]
        elif query in self.crawlers:
            id = getattr(self.crawlers[query], '__id__')
            info = self._index.crawlers[id]
        else:
            ids = self._store.search(normalize(query))
            if len(ids) != 1:
                return None
            info = self._index.crawlers[ids[0]]
        return SourceItem(
            info=info,
            crawler=self.crawlers[info.id],
        )
