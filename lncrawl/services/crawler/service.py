import logging
from typing import List, Optional

from pydantic import HttpUrl
from sqlmodel import select

from ...context import ctx
from ...dao import Chapter, Novel, Volume
from ...exceptions import ServerErrors
from .dto import LoginData
from .utils import format_novel

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    def fetch_novel(self, url: HttpUrl, login: Optional[LoginData]) -> Novel:
        if not url.host:
            raise ServerErrors.invalid_url

        # fetch novel metadata
        novel_url = url.encoded_string()
        crawler = ctx.sources.create_crawler(novel_url)
        if login and getattr(crawler, "can_login", False):
            logger.debug(f"Login: {login}")
            crawler.login(login.username, login.password)

        crawler.read_novel_info()
        format_novel(crawler)

        # save to database
        with ctx.db.session() as sess:
            # get or create novel
            novel = sess.exec(
                select(Novel)
                .where(Novel.url == novel_url)
            ).first()
            if not novel:
                novel = Novel(
                    url=novel_url,
                    domain=url.host,
                    title=crawler.novel_title,
                )
                sess.add(novel)
                sess.refresh(novel)

            # update novel
            novel.title = crawler.novel_title
            novel.authors = crawler.novel_author
            novel.cover = crawler.novel_cover
            novel.manga = crawler.has_manga
            novel.mtl = crawler.has_mtl
            novel.synopsis = crawler.novel_synopsis
            novel.tags = crawler.novel_tags
            novel.rtl = crawler.is_rtl
            novel.language = crawler.language
            novel.volume_count = len(crawler.volumes)
            novel.chapter_count = len(crawler.chapters)
            sess.commit()

            # add or update volumes
            volumes = sess.exec(
                select(Volume)
                .where(Volume.novel_id == novel.id)
            ).all()
            volumes_map = {v.serial: v for v in volumes}
            new_volumes: List[Volume] = []
            for v in crawler.volumes:
                if v.id in volumes_map:
                    volume = volumes_map[v.id]
                    volume.title = v.title
                else:
                    volume = Volume(
                        novel_id=novel.id,
                        serial=v.id,
                        title=v.title,
                    )
                    volumes_map[v.id] = volume
                    new_volumes.append(volume)
            sess.add_all(new_volumes)
            sess.commit()

            # add or update chapters
            chapters = sess.exec(
                select(Chapter)
                .where(Chapter.novel_id == novel.id)
            ).all()
            chapters_map = {c.serial: c for c in chapters}
            new_chapters: List[Chapter] = []
            for c in crawler.chapters:
                volume = volumes_map.get(c.volume or 0)
                if c.id in chapters_map:
                    chapter = chapters_map[c.id]
                    if volume:
                        chapter.volume_id = volume.id
                    if not chapter.crawled:
                        chapter.title = c.title
                else:
                    chapter = Chapter(
                        novel_id=novel.id,
                        serial=c.id,
                        title=c.title,
                        url=c.url,
                    )
                    if volume:
                        chapter.volume_id = volume.id
                    new_chapters.append(chapter)
            sess.add_all(new_chapters)
            sess.commit()

        return novel
