import logging
from typing import Optional

from pydantic import HttpUrl
from sqlmodel import select

from ...context import ctx
from ...dao import Chapter, ChapterImage, Novel
from ...exceptions import ServerErrors
from ...models import Chapter as ChapterModel
from .dto import LoginData
from .utils import download_cover, download_image, format_novel

logger = logging.getLogger(__name__)


class CrawlerService:
    def __init__(self) -> None:
        pass

    def get_crawler(self, novel_url: str, login: Optional[LoginData] = None):
        crawler = ctx.sources.create_crawler(novel_url)
        can_login = getattr(crawler, "can_login", False)
        logged_in = getattr(crawler, "__logged_in__", False)
        if login and can_login and not logged_in:
            logger.debug(f"Login: {login}")
            crawler.login(login.username, login.password)
            setattr(crawler, "__logged_in__", True)
        return crawler

    def fetch_novel(self, url: HttpUrl, login: Optional[LoginData] = None) -> Novel:
        # get crawler
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = url.encoded_string()
        crawler = self.get_crawler(novel_url, login)

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

        return novel

    def fetch_chapter(self, chapter: Chapter, login: Optional[LoginData] = None) -> Chapter:
        # get crawler
        url = HttpUrl(chapter.url)
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = ctx.novels.get(chapter.novel_id).url
        crawler = self.get_crawler(novel_url, login)

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
        ctx.chapter_images.sync(chapter.novel_id, chapter.id, model.images)

        # update db
        with ctx.db.session() as sess:
            sess.refresh(chapter)
            chapter.crawled = bool(model.body)
            sess.commit()

        return chapter

    def fetch_image(self, image: ChapterImage, login: Optional[LoginData] = None) -> ChapterImage:
        # get crawler
        url = HttpUrl(image.url)
        if not url.host:
            raise ServerErrors.invalid_url
        novel_url = ctx.novels.get(image.novel_id).url
        crawler = self.get_crawler(novel_url, login)

        # download image
        file = ctx.files.resolve(image.image_file)
        download_image(crawler, url.encoded_string(), file)

        # update db
        with ctx.db.session() as sess:
            sess.refresh(image)
            image.crawled = file.is_file()
            sess.commit()

        return image
