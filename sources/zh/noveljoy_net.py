# -*- coding: utf-8 -*-
import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class NoveljoyNetCrawler(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = ["https://noveljoy.net/"]
    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        super().initialize()
        self.init_executor(1)

    def select_search_items(self, query: str) -> Generator[Tag, None, None]:
        # Select novel items found in search page from the query
        #
        # Example:
        #   params = {"searchkey": query}
        #   soup = self.post_soup(f"{self.home_url}search?{urlencode(params)}")
        #   yield from soup.select(".col-content .con .txt h3 a")
        yield from []

    def parse_search_item(self, tag: Tag) -> SearchResult:
        # Parse a tag and return single search result
        # The tag here comes from self.select_search_items
        return SearchResult(
            title=tag.get_text(strip=True),
            url=self.absolute_url(tag["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        # Parse and return the novel title
        #
        # Example:
        # tag = soup.select_one(".post-title")
        # assert tag, 'No title tag'
        # return tag.get_text(strip=True)
        raise NotImplementedError()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        # Parse and return the novel cover
        #
        # Example:
        # tag = soup.select_one("img[src]")
        # if not tag:
        #     return ""
        # return self.absolute_url(tag["src"])
        raise NotImplementedError()

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        # Parse and return the novel authors
        #
        # Example 1: <single author>
        #   tag = soup.find(string="Author:")
        #   if tag:
        #       yield tag.get_text(strip=True)
        #
        # Example 2: <multiple authors>
        #   for a in soup.select("a[href*='/author/']"):
        #       yield a.get_text(strip=True)
        yield from []

    def parse_genres(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        # Parse and return the novel categories or tags
        yield from []

    def parse_summary(self, soup: BeautifulSoup) -> str:
        # Parse and return the novel summary or synopsis
        return ''

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        # Select chapter list item tags from page soup
        #
        # Example:
        # yield from soup.select("table > li > a")
        yield from []

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        # Parse a single chapter from `select_chapter_tags` result
        #
        # Example:
        return Chapter(
            id=id,
            title=tag.get_text(strip=True),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        # Select the tag containing the chapter content text
        #
        # Example:
        # return soup.select_one(".chapter-content")
        raise NotImplementedError()
