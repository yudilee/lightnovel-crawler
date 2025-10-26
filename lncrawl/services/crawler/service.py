import logging
from typing import List, Optional

from pydantic import HttpUrl
from sqlmodel import select

from ...context import ctx
from ...dao import Chapter, Novel, Volume
from ...exceptions import ServerErrors
from ...models import Chapter as ChapterModel
from .dto import LoginData
from .utils import download_cover, download_image, format_novel, save_chapter

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    def fetch_novel(self, url: HttpUrl, login: Optional[LoginData]) -> Novel:
        # get crawler
        if not url.host:
            raise ServerErrors.invalid_url
        base_url = f"{url.scheme}://{url.host}/"
        crawler = ctx.sources.create_crawler(base_url)

        # fetch novel metadata
        crawler.novel_url = url.encoded_string()
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
                .where(Novel.url == crawler.novel_url)
            ).first()
            if not novel:
                novel = Novel(
                    domain=url.host,
                    url=crawler.novel_url,
                    title=crawler.novel_title,
                )
                sess.add(novel)
                sess.refresh(novel)

            # update novel
            novel.title = crawler.novel_title
            novel.authors = crawler.novel_author
            novel.cover_url = crawler.novel_cover
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

            # download cover
            novel.cover_file = download_cover(crawler, novel.id)
            sess.commit()

        return novel

    def fetch_chapter(self, chapter: Chapter, login: Optional[LoginData]) -> Chapter:
        # get crawler
        url = HttpUrl(chapter.url)
        if not url.host:
            raise ServerErrors.invalid_url
        base_url = f"{url.scheme}://{url.host}/"
        crawler = ctx.sources.create_crawler(base_url)

        # prepare crawler
        crawler.novel_url = url.encoded_string()
        if login and getattr(crawler, "can_login", False):
            logger.debug(f"Login: {login}")
            crawler.login(login.username, login.password)

        # get chapter content
        model = ChapterModel(
            id=chapter.serial,
            title=chapter.title,
            url=url.encoded_string(),
        )
        model.body = crawler.download_chapter_body(model)
        crawler.extract_chapter_images(model)

        # save chapter content
        content_file = save_chapter(
            chapter.novel_id,
            chapter.id,
            model.body or ''
        )

        # download images
        futures = [
            crawler.executor.submit(
                download_image, crawler, url, filename
            )
            for (filename, url) in model.images.items()
        ]
        images = [
            file_path
            for file_path in crawler.resolve_futures(
                futures,
                disable_bar=True,
            )
            if file_path
        ]

        # update db
        with ctx.db.session() as sess:
            sess.refresh(chapter)
            chapter.images = images
            chapter.crawled = bool(model.body)
            chapter.content_file = content_file
            sess.commit()

        return chapter
