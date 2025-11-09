import json
import logging
import os
from threading import Event
from typing import Optional, Union

from pydantic import HttpUrl
from sqlmodel import select

from ...context import ctx
from ...dao import Chapter, ChapterImage, Novel
from ...dao.enums import SecretType
from ...exceptions import ServerErrors
from ...models import Chapter as ChapterModel
from ...utils.url_tools import extract_host
from .dto import LoginData
from .utils import download_cover, download_image, format_novel

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    def save_login(self, url: str, login: LoginData) -> None:
        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        value = json.dumps([login.username, login.password], ensure_ascii=False)
        ctx.secrets.add(SecretType.LOGIN, host, value)

    def get_login(self, url: str) -> Optional[LoginData]:
        host = extract_host(url)
        if not host:
            raise ServerErrors.invalid_url
        value = ctx.secrets.get_random_value(host)
        if not value:
            return None
        [username, password] = json.loads(value)
        return LoginData(username=username, password=password)

    def get_crawler(self, novel_url: str):
        crawler = ctx.sources.create_crawler(novel_url)
        can_login = getattr(crawler, "can_login", False)
        logged_in = getattr(crawler, "__logged_in__", False)
        if can_login and not logged_in:
            login = self.get_login(novel_url)
            if login:
                crawler.login(login.username, login.password)
                setattr(crawler, "__logged_in__", True)
        return crawler

    def fetch_novel(self, url: Union[str, HttpUrl], signal=Event()) -> Novel:
        if isinstance(url, str):
            url = HttpUrl(url)

        # get crawler
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = url.encoded_string()
        crawler = self.get_crawler(novel_url)
        crawler_version = getattr(crawler, 'version')
        crawler.scraper.signal = signal

        # fetch novel metadata
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
            novel.extra['crawler_version'] = crawler_version
            sess.add(novel)
            sess.commit()

        # add or update tags
        ctx.tags.insert(novel.tags)

        # add or update volumes
        ctx.volumes.sync(novel.id, crawler.volumes)

        # add or update volumes
        ctx.chapters.sync(novel.id, crawler.chapters)

        # download cover
        download_cover(crawler, ctx.files.resolve(novel.cover_file))

        # update output path time
        novel_path = ctx.files.resolve(f'novels/{novel.id}')
        if novel_path.is_dir():
            os.utime(novel_path)

        return novel

    def fetch_chapter(self, chapter_id: str, signal=Event()) -> Chapter:
        chapter = ctx.chapters.get(chapter_id)

        # get crawler
        url = HttpUrl(chapter.url)
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = ctx.novels.get(chapter.novel_id).url
        crawler = self.get_crawler(novel_url)
        crawler_version = getattr(crawler, 'version')
        crawler.scraper.signal = signal

        # check if download is necessary
        if chapter.is_available and chapter.extra.get('crawler_version') == crawler_version:
            return chapter

        # get chapter content
        model = ChapterModel(
            id=chapter.serial,
            title=chapter.title,
            url=url.encoded_string(),
            extras=chapter.extra,
        )
        model.body = crawler.download_chapter_body(model).strip()
        crawler.extract_chapter_images(model)

        # save chapter content
        ctx.files.save_text(chapter.content_file, model.body)

        # save chapter images
        ctx.images.sync(chapter, model.images)

        # update db
        with ctx.db.session() as sess:
            chapter.is_done = bool(model.body)
            chapter.extra['crawler_version'] = crawler_version
            sess.add(chapter)
            sess.commit()

        return chapter

    def fetch_image(self, image_id: str, signal=Event()) -> ChapterImage:
        image = ctx.images.get(image_id)

        # get crawler
        url = HttpUrl(image.url)
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = ctx.novels.get(image.novel_id).url
        crawler = self.get_crawler(novel_url)
        crawler_version = getattr(crawler, 'version')
        crawler.scraper.signal = signal

        # check if download is necessary
        if image.is_available and image.extra.get('crawler_version') == crawler_version:
            return image

        # download image
        file = ctx.files.resolve(image.image_file)
        download_image(crawler, url.encoded_string(), file)

        # update db
        with ctx.db.session() as sess:
            image.is_done = file.is_file()
            image.extra['crawler_version'] = crawler_version
            sess.add(image)
            sess.commit()

        return image
