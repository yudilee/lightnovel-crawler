import asyncio
import gzip
import io
import json
import logging
import shutil
from typing import Any, Dict, Optional, Type

from ...context import ctx
from ...core.crawler import Crawler
from . import utils

logger = logging.getLogger(__name__)


class Sources:
    def __init__(self) -> None:
        self._index: Dict[str, Any] = {}
        self.updater: Optional[asyncio.Task] = None
        self.rejected: Dict[str, str] = {}
        self.crawlers: Dict[str, Type[Crawler]] = {}

    def cleanup(self):
        if self.updater:
            self.updater.cancel()
        self.rejected.clear()
        self.crawlers.clear()

    def prepare(self):
        # get local index
        local_file = ctx.config.crawler.local_index_file
        local_index = utils.load_json(local_file)

        # get saved index (copy local if not exists)
        user_file = ctx.config.crawler.user_index_file
        if user_file.is_file():
            user_index = utils.load_json(user_file)
        else:
            user_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(local_file, user_file)
            user_index = local_index

        # get latest index (copy local to user if local is latest)
        if user_index['v'] < local_index['v']:
            shutil.copy2(local_file, user_file)
            user_index = local_index

        # load crawlers from the index
        self.load_index(user_index)

        # run background task to update sources
        if self.updater:
            self.updater.cancel()
        self.updater = asyncio.run(self.update())

    async def update(self):
        try:
            # fetch online index
            compressed = await utils.fetch(ctx.config.crawler.index_file_download_url)
            with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode='rb') as fp:
                online_index = json.loads(fp.read().decode())

            # return if online index is not latest
            if online_index['v'] <= self._index['v']:
                logger.info('No latest updates found')
                return

            # save the latest index
            user_file = ctx.config.crawler.user_index_file
            utils.save_json(user_file, self._index)

            # download updated source files
            tasks = []
            for sid, source in online_index['crawlers'].items():
                current = self._index['crawlers'].get(sid)
                if current and current['version'] >= source['version']:
                    continue
                source_file = user_file.parent.parent / str(source['file_path'])
                task = utils.download(source['url'], source_file)
                tasks.append(task)
            await asyncio.gather(*tasks)

            # load the online index
            self.load_index(online_index)
            logger.info('Source update done')
        except asyncio.CancelledError:
            logger.info('Source updater canceled')

    def load_index(self, index: Dict[str, Any]) -> None:
        self._index = index

        # clear caches
        self.rejected.clear()
        self.crawlers.clear()

        # update rejected list
        for url, reason in index['rejected'].items():
            for key in utils.get_keys(url):
                self.rejected[key] = reason

        # dynamically import all crawlers
        user_path = ctx.config.crawler.user_index_file.parent.parent
        local_path = ctx.config.crawler.local_index_file.parent.parent
        for source in index['crawlers'].values():
            crawlers = utils.import_crawlers(user_path / str(source['file_path']))
            crawlers += utils.import_crawlers(local_path / str(source['file_path']))
            for crawler in crawlers:
                upcoming_time = getattr(crawler, 'modified_at')
                for key in utils.get_keys(crawler.base_url):
                    # do not update if the current crawler is the latest
                    if key in self.crawlers:
                        current_time = getattr(self.crawlers[key], 'modified_at')
                        if current_time >= upcoming_time:
                            continue
                    # update cache
                    self.crawlers[key] = crawler
