import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Dict, Optional

import httpx

from ..context import ctx
from ..exceptions import ServerErrors
from ..utils.platforms import Platform
from ..utils.url_tools import extract_base

logger = logging.getLogger(__name__)


class FetchService:
    def __init__(self) -> None:
        self._favicons: Dict[str, Optional[Path]] = {}
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

    def download(self, url: str, file: Path) -> None:
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

    def favicon(self, url: str) -> Path:
        favicon_url = f'{extract_base(url)}favicon.ico'

        if favicon_url in self._favicons:
            cache = self._favicons[favicon_url]
            if not cache:
                raise ServerErrors.invalid_image_response
            return cache

        try:
            filename = hashlib.md5(favicon_url.encode()).hexdigest()
            out_file = ctx.files.resolve(f'/images/{filename}.ico')
            self._favicons[favicon_url] = out_file
            if out_file.is_file():
                return out_file

            self.download(favicon_url, out_file)
            return out_file
        except Exception as e:
            self._favicons[favicon_url] = None
            raise ServerErrors.invalid_image_response from e
