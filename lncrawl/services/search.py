import logging
from concurrent.futures import Future
from difflib import SequenceMatcher
from threading import Event
from typing import List, Optional, Set, Type

from slugify import slugify

from ..context import ctx
from ..core.crawler import Crawler
from ..core.taskman import TaskManager
from ..models import CombinedSearchResult, SearchResult

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        pass

    def search(
        self,
        query: str,
        limit: int = 10,
        concurrency: int = 10,
        timeout: float = 30,
    ) -> List[CombinedSearchResult]:
        """Perform separate search across sources."""
        ctx.sources.ensure_load()
        constructors = set(
            [item.crawler for item in ctx.sources.list(can_search=True)]
        )

        logger.info(f'Searching {len(constructors)} sources for "{query}"')
        signal = Event()
        taskman = TaskManager(concurrency, signal=signal)

        # Submit search tasks
        futures: List[Future[List[SearchResult]]] = []
        for constructor in constructors:
            future = taskman.submit_task(self._search_job, constructor, query, signal)
            futures.append(future)

        # Wait for all tasks to finish with progress
        records: List[SearchResult] = []
        try:
            for result_list in taskman.resolve_as_generator(
                futures,
                unit="source",
                desc="Searching",
                signal=signal,
                timeout=timeout,
                disable_bar=True,
            ):
                if result_list:
                    logger.info(f"Got {len(result_list)} results from a source")
                    records.extend(result_list)
        except KeyboardInterrupt:
            signal.set()
        except Exception as e:
            logger.error(f"Failed to perform search! {e}", exc_info=True)
        finally:
            signal.set()
            taskman.shutdown()
        
        logger.info(f"Total records found: {len(records)}")

        # Combine the search results
        combined: dict[str, List[SearchResult]] = {}
        for item in records:
            if not (item and item.title):
                continue
            key = slugify(str(item.title))
            if len(key) <= 2:
                continue
            combined.setdefault(key, [])
            combined[key].append(item)

        # Process combined search results
        results: List[CombinedSearchResult] = []
        for key, value in combined.items():
            value.sort(key=lambda x: x.url)
            results.append(
                CombinedSearchResult(
                    id=key,
                    title=value[0].title,
                    novels=value,
                )
            )

        # Sort by relevance (number of sources, then similarity to query)
        results.sort(
            key=lambda x: (
                -len(x.novels),
                -SequenceMatcher(a=x.title, b=query).ratio(),
            )
        )

        return results[:limit]

    def _search_job(
        self, constructor: Type[Crawler], query: str, signal: Event
    ) -> List[SearchResult]:
        if hasattr(constructor, "url"):
            url = constructor.url
        elif hasattr(constructor, "base_url"):
            url = constructor.base_url[0]
            setattr(constructor, "url", url)
        else:
            url = "Unknown"
            setattr(constructor, "url", url)
        logger.info(f"[{url}] Starting search for '{query}'")
        try:
            crawler = ctx.sources.init_crawler(constructor)
            crawler.scraper.signal = signal
            results = crawler.search_novel(query)
            results = [SearchResult(**item) for item in results]
            logger.debug(f"[{url}] Found {len(results)} results")
            crawler.close()
            return results
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"[{url}] Search failed: {e}", exc_info=True)
        return []
