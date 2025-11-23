import logging
from typing import Optional

from bs4 import Tag

from lncrawl.exceptions import LNException
from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class Arcanetranslations(MangaStreamTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://arcanetranslations.com/"]

    def select_chapter_body(self, tag) -> Optional[Tag]:
        result = super().select_chapter_body(tag)
        if not result:
            raise LNException('No chapter content')
        if "Login to buy access to this content" in result.text:
            raise LNException("This content is behind a paywall. Please login to access it.")
        return result
