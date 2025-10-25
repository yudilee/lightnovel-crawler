import re
from enum import Enum
from typing import List, Optional

import questionary
import typer
from rich import print

from ...assets.languages import language_codes
from ...context import ctx
from ...utils.url_tools import extract_host, validate_url, extract_base
from .app import app


class Feature(str, Enum):
    has_manga = "manga"
    has_mtl = "mtl"
    can_search = "search"
    can_login = "login"


@app.command("create", help="Create a source.")
def create_one(
    non_interactive: bool = typer.Option(
        False,
        '--noin',
        help='Disable interactive mode',
    ),
    locale: Optional[str] = typer.Option(
        None,
        '-l', '--locale',
        help='Content language (ISO 639-1 code)',
    ),
    features: Optional[List[Feature]] = typer.Option(
        None,
        "-f", "--features",
        help='Crawler features. e.g.: -f search -f mtl',
    ),
    url: str = typer.Argument(
        default=None,
        help="The URL of the source website.",
    ),
):
    # validate host
    host = extract_host(url)
    if not host:
        if non_interactive:
            print(f'[red]Invalid URL: {url}[/red]')
            return
        url = _prompt_url()
        host = extract_host(url)
        if not host:
            return

    # check if already exists
    item = ctx.sources.get(host)
    if item:
        print(
            '[green]A crawler is already available for '
            f'[b]{host}[/b]:[/green] [cyan]{item.info.local_file}[/cyan]'
        )
        return

    # ensure locale
    if locale is None:
        locale = '' if non_interactive else _prompt_locale()

    # build crawler name and file_name
    name = ' '.join(host.split('.')).title()
    name = re.sub(r'[^A-Za-z0-9]', '_', name)
    file_name = name.casefold()
    name = name.replace('_', '')
    name += 'Crawler'

    # check file path
    file_path = _build_path(locale, file_name)
    if file_path.is_file() and (non_interactive or not _prompt_replace(str(file_path))):
        print(
            '[red]A file already exists for '
            f'[b]{host}[/b]:[/red] [cyan]{file_path}[/cyan]'
        )
        return

    # ensure capabilities
    if features is None:
        if non_interactive:
            features = []
        else:
            features = _prompt_features()

    # generate content
    content = _generate_content(
        name=name,
        features=features,
        base_url=extract_base(url),
    )

    # save content
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding='utf-8')
    print(
        '[green]Created crawler for '
        f'[b]{host}[/b]:[/green] [cyan]{file_path}[/cyan]'
    )


def _build_path(locale: str, file_name: str):
    file_path = ctx.config.crawler.local_index_file.parent
    file_path /= locale or 'multi'
    if locale == 'en':
        file_path /= file_name[0]
    file_path /= file_name + '.py'
    return file_path


def _prompt_url() -> str:
    print('[i]The URL must start with [cyan]http[/cyan] or [cyan]https[/cyan]:[/i]')
    return questionary.text(
        "Website URL:",
        qmark="🌐",
        validate=validate_url,
    ).ask()


def _prompt_locale() -> str:
    choices = [
        f"[{c:02}] {n}"
        for c, n in sorted(language_codes.items())
    ]

    print('[i]Leave empty if locale is unknown or content is in multiple language:[/i]')
    language = questionary.autocomplete(
        'Enter language (ISO 639-1 code)',
        choices=choices,
        validate=lambda s: (s in choices) or (s in language_codes)
    ).ask()

    if len(language) > 2:
        language = language[1:3].strip()
    return language


def _prompt_features() -> List[Feature]:
    selected = questionary.checkbox(
        "Enable features:",
        choices=list(Feature),
    ).ask()
    return [Feature(v) for v in selected]


def _prompt_replace(file: str) -> List[Feature]:
    return questionary.confirm(
        "Crawler file already exists. Do you want to replace it?",
        instruction=file,
        default=False
    ).ask()


def _generate_content(name: str, base_url: str, features: List[Feature]):
    content = '''# -*- coding: utf-8 -*-
import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag

'''

    if Feature.can_search in features:
        content += '''from lncrawl.models import Chapter, SearchResult'''
    else:
        content += '''from lncrawl.models import Chapter'''

    content += f'''
from lncrawl.templates.soup.chapter_only import ChapterOnlySoupTemplate
from lncrawl.templates.soup.searchable import SearchableSoupTemplate

logger = logging.getLogger(__name__)


class {name}(SearchableSoupTemplate, ChapterOnlySoupTemplate):
    base_url = ["{base_url}"]
    has_manga = {Feature.has_manga in features}
    has_mtl = {Feature.has_manga in features}

    def initialize(self) -> None:
        # You can customize `TextCleaner` and other necessary things.
        super().initialize()
'''

    if Feature.can_login in features:
        content += '''
    def login(self, username_or_email: str, password_or_token: str) -> None:
        # Add logic to login. For example: sources/en/l/lnmtl.py
        pass
'''

    if Feature.can_search in features:
        content += '''
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
'''

    content += '''
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
        # Select chapter list item tags from the page soup
        #
        # Example:
        # yield from soup.select("table > li > a")
        yield from []

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        # Parse a single chapter from chapter list item tag
        #
        # Example:
        return Chapter(
            id=id,
            title=tag.get_text(strip=True),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        # Select the tag containing the chapter text
        #
        # Example:
        # return soup.select_one(".chapter-content")
        raise NotImplementedError()
'''

    return content
