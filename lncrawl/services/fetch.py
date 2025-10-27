import logging
import os
import time
from pathlib import Path

import httpx

from ..context import ctx
from ..utils.platforms import Platform

logger = logging.getLogger(__name__)


class FetchService:
    def __init__(self) -> None:
        pass

    def _client(self):
        name = ctx.config.app.name
        version = ctx.config.app.version
        user_agent = f"{''.join(name.split(' '))}/{version} ({Platform.name})"
        return httpx.Client(
            http2=True,
            follow_redirects=True,
            headers={"User-Agent": user_agent},
        )

    def get(self, url: str) -> bytes:
        with self._client() as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.content

    def download(self, url: str, file: Path) -> Path:
        content = self.get(url)
        file.parent.mkdir(parents=True, exist_ok=True)
        tid = time.thread_time_ns() % 1000
        tmp = file.with_suffix(f'{file.suffix}.tmp{tid}')
        try:
            tmp.write_bytes(content)
            os.replace(tmp, file)
        finally:
            tmp.unlink(missing_ok=True)
        logger.debug(f'Downloaded: {file}')
        return file
