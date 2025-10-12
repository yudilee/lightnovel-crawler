import hashlib
import importlib.util
import json
import logging
import os
import re
import time
from pathlib import Path
from threading import Semaphore
from typing import List, Set, Type, Union
from urllib.parse import urlparse

import httpx

from ...context import ctx
from ...core.crawler import Crawler
from ...utils.platforms import Platform

logger = logging.getLogger(__name__)

__semaphone = Semaphore(5)
__url_regex = re.compile(r"^^(https?|ftp)://[^\s/$.?#].[^\s]*$", re.I)


async def fetch(url: str) -> bytes:
    logger.info(f"Downloading: {url}")
    name = ctx.config.app.name
    version = ctx.config.app.version
    user_agent = f"{''.join(name.split(' '))}/{version} ({Platform.name})"
    async with httpx.AsyncClient(
        http2=True,
        follow_redirects=True,
        headers={"User-Agent": user_agent},
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


async def download(url: str, file: Path) -> None:
    with __semaphone:
        file.parent.mkdir(parents=True, exist_ok=True)
        tid = time.thread_time_ns() % 1000
        tmp = file.with_suffix(f'{file.suffix}.tmp{tid}')
        content = await fetch(url)
        tmp.write_bytes(content)
        os.replace(tmp, file)
        logger.debug(f'File saved: {file}')


def can_do(crawler: Type[Crawler], prop_name: str):
    '''Checks if crawler has implemented the given property name'''
    if not hasattr(crawler, prop_name):
        return False
    if not hasattr(Crawler, prop_name):
        return True
    return getattr(crawler, prop_name) != getattr(Crawler, prop_name)


def has_method(crawler: Type[Crawler], method: str):
    '''Checks if crawler has a callable method'''
    return hasattr(crawler, method) and callable(getattr(crawler, method))


def get_keys(urls: Union[str, List[str]]) -> Set[str]:
    keys = []
    for url in ([urls] if isinstance(urls, str) else urls):
        url_host = urlparse(url).hostname
        no_www = url.replace("://www.", "://")
        no_www_host = urlparse(no_www).hostname
        keys += [url, no_www, url_host, no_www_host]
    return set(filter(None, keys))


def load_json(file: Path):
    with open(file, encoding='utf-8') as f:
        return json.load(f)


def save_json(file: Path, content):
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False)


def import_crawlers(file: Path) -> List[Type[Crawler]]:
    # validate the file
    if not file.is_file():
        return []
    file = file.absolute()

    # import modules from the file
    try:
        module_name = hashlib.md5(file.stem.encode()).hexdigest()
        spec = importlib.util.spec_from_file_location(module_name, file)
        if not (spec and spec.loader):
            logger.info(f"[{file}] Unexpected spec")
            return []
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        logger.info(f"[{file}] Failed to load: {repr(e)}")
        return []

    # import all valid crawlers
    crawlers = []
    for key in dir(module):
        crawler = getattr(module, key)

        # type checks
        if (
            crawler is Crawler
            or type(crawler) is not type(Crawler)
            or not issubclass(crawler, Crawler)
            or crawler.__dict__.get("is_template")
            or getattr(crawler, '__module__', '') != module_name
        ):
            continue

        # required method checks
        if not has_method(crawler, 'read_novel_info'):
            logger.info(f"[{file}] Missing required method 'read_novel_info'")
            continue
        if not has_method(crawler, 'download_chapter_body'):
            logger.info(f"[{file}] Missing required method 'download_chapter_body'")
            continue

        # base url checks
        base_url = getattr(crawler, "base_url", [])
        urls = [base_url] if isinstance(base_url, str) else base_url
        urls = [str(url).lower().strip("/") + "/" for url in urls]
        urls = [url for url in set(urls) if __url_regex.match(url)]
        if not urls:
            logger.info(f"[{file}] No base url: {crawler}")
            continue

        # static values
        setattr(crawler, "base_url", urls)
        setattr(crawler, "can_login", can_do(crawler, 'login'))
        setattr(crawler, "can_logout", can_do(crawler, 'logout'))
        setattr(crawler, "can_search", can_do(crawler, 'search_novel'))

        # other metdata
        setattr(crawler, "file_path", str(file.absolute()))
        setattr(crawler, "created_at", file.stat().st_ctime)
        setattr(crawler, "modified_at", file.stat().st_mtime)

        crawlers.append(crawler)

    if not crawlers:
        logger.info(f"[{file}] No crawler found")
    return crawlers
