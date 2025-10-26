import hashlib
import logging
from abc import abstractmethod
from typing import List, Optional, Union

from ..context import ctx
from ..models import Chapter, SearchResult, Volume
from .cleaner import TextCleaner
from .scraper import Scraper

logger = logging.getLogger(__name__)


class Crawler(Scraper):
    """Blueprint for creating new crawlers"""

    base_url: Union[str, List[str]]
    has_manga = False
    has_mtl = False
    language = ""

    is_disabled = False
    disable_reason: Optional[str] = None

    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> None:
        """
        Creates a standalone Crawler instance.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 10.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        self.cleaner = TextCleaner()

        # Available in `search_novel` or `read_novel_info`
        self.novel_url = ""

        # Must resolve these fields inside `read_novel_info`
        self.novel_title: str = ""
        self.novel_author: str = ""
        self.novel_cover: Optional[str] = None
        self.is_rtl: bool = False
        self.novel_synopsis: str = ""
        self.novel_tags: List[str] = []

        # Each item must contain these keys:
        # `id` - 1 based index of the volume
        # `title` - the volume title (can be ignored)
        self.volumes: List[Volume] = []

        # Each item must contain these keys:
        # `id` - 1 based index of the chapter
        # `title` - the title name
        # `volume` - the volume id of this chapter
        # `volume_title` - the volume title (can be ignored)
        # `url` - the link where to download the chapter
        self.chapters: List[Chapter] = []

        # Initialize superclass
        super().__init__(
            origin=self.base_url[0],
            workers=workers,
            parser=parser,
        )

    def close(self) -> None:
        # if hasattr(self, "volumes"):
        #     self.volumes.clear()
        # if hasattr(self, "chapters"):
        #     self.chapters.clear()
        super().close()

    # ------------------------------------------------------------------------- #
    # Methods to implement in crawler
    # ------------------------------------------------------------------------- #

    def initialize(self) -> None:
        pass

    def login(self, username_or_email: str, password_or_token: str) -> None:
        pass

    def search_novel(self, query: str) -> List[SearchResult]:
        """Gets a list of results matching the given query"""
        raise NotImplementedError()

    @abstractmethod
    def read_novel_info(self) -> None:
        """Get novel title, author, cover, volumes and chapters"""
        raise NotImplementedError()

    @abstractmethod
    def download_chapter_body(self, chapter: Chapter) -> str:
        """Download body of a single chapter and return as clean html format."""
        raise NotImplementedError()

    # ------------------------------------------------------------------------- #
    # Utility methods that can be overriden
    # ------------------------------------------------------------------------- #

    def index_of_chapter(self, url: str) -> int:
        """Return the index of chapter by given url or 0"""
        url = self.absolute_url(url)
        for chapter in self.chapters:
            if chapter.url.rstrip("/") == url:
                return chapter.id
        return 0

    def extract_chapter_images(self, chapter: Chapter) -> None:
        if ctx.config.crawler.ignore_images or not chapter.body:
            return

        has_changes = False
        chapter.setdefault("images", {})
        soup = self.make_soup(chapter.body)
        for img in soup.select("img[src]"):
            src_url = img.get('src')
            if not isinstance(src_url, str):
                continue

            full_url = self.absolute_url(src_url, page_url=chapter["url"])
            if not full_url.startswith("http"):
                continue

            filename = hashlib.md5(full_url.encode()).hexdigest() + ".jpg"
            img.attrs = {"src": "images/" + filename, "alt": filename}
            chapter.images[filename] = full_url
            has_changes = True

        if has_changes:
            body = soup.find("body")
            assert body
            chapter.body = body.decode_contents()
