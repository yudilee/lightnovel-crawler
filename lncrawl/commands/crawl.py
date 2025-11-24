import logging
from typing import List, Optional, Dict

import questionary
import typer
from rich import print
from rich.console import Console
from rich.panel import Panel

from ..context import ctx
from ..dao import Novel, Artifact
from ..dao.enums import OutputFormat
from ..exceptions import ServerError
from ..utils.file_tools import format_size, open_folder
from ..utils.url_tools import validate_url

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)


@app.command(
    help='Crawl from novel page URL.'
)
def crawl(
    non_interactive: bool = typer.Option(
        False,
        '--noin',
        help='Disable interactive mode',
    ),
    range_all: Optional[bool] = typer.Option(
        None,
        '--all',
        is_flag=True,
        help='Download all chapters'
    ),
    range_first: Optional[int] = typer.Option(
        None,
        '--first',
        min=1,
        metavar='N',
        help='Download first few chapters'
    ),
    range_last: Optional[int] = typer.Option(
        None,
        '--last',
        min=1,
        metavar='N',
        help='Download latest few chapters',
    ),
    formats: List[OutputFormat] = typer.Option(
        [],
        '-f', '--format',
        show_choices=True,
        help='Output formats',
    ),
    url: str = typer.Argument(
        default=None,
        help="Novel details page URL.",
    ),
):
    # ensure url
    if not url:
        if non_interactive:
            print('[red]Please enter a novel page URL[/red]')
            return
        url = _prompt_url()

    # init crawler
    try:
        crawler = ctx.sources.init_crawler(url)
    except ServerError as e:
        print(f'[red]{e.format(True)}[/red]')
        return

    # fetch novel details
    with console.status('Fetching novel details...'):
        user = ctx.users.get_admin()
        novel = ctx.crawler.fetch_novel(user.id, url, crawler=crawler)
    print(Panel('\n'.join(filter(None, [
        f'[cyan]{novel.url}[/cyan]',
        f'[yellow][b]{novel.title}[/b][/yellow]',
        f'[green]{novel.authors}[/green]' if novel.authors else None,
        f'[i]{novel.volume_count} volumes, {novel.chapter_count} chapters[/i]'
    ]))))

    if novel.chapter_count == 0:
        print('[red]No chapters to download[/red]')
        return

    # select chapters to download
    chapters: List[str] = []
    if not non_interactive and all([
        range_all is None,
        range_first is None,
        range_last is None,
    ]):
        chapters = _prompt_chapter_selection(novel)
    else:
        chapters = ctx.chapters.list_ids(
            novel_id=novel.id,
            descending=bool(range_last),
            limit=range_last or range_first
        )
    if not chapters:
        print('[red]No chapters to download[/red]')
        return

    # select formats to bind
    if not formats:
        if non_interactive:
            formats = list(OutputFormat)
        else:
            formats = _prompt_format_selection()

    # download chapters
    chapter_futures = [
        crawler.submit_task(
            ctx.crawler.fetch_chapter,
            user.id,
            chapter_id,
            crawler=crawler
        ) for chapter_id in sorted(set(chapters))
    ]
    chapter_image_ids = []
    for chapter in crawler.resolve_as_generator(
        chapter_futures,
        desc='Chapters',
        unit=' c'
    ):
        if not chapter:
            continue
        chapter_image_ids += ctx.images.list_ids(chapter_id=chapter.id)

    # download chapter images
    image_futures = [
        crawler.submit_task(
            ctx.crawler.fetch_image,
            user.id,
            image_id,
            crawler=crawler
        ) for image_id in sorted(set(chapter_image_ids))
    ]
    crawler.resolve_futures(
        image_futures,
        desc='Images',
        unit=' img'
    )

    # create artifacts
    artifacts: Dict[OutputFormat, Artifact] = {}
    if ctx.binder.depends_on_epub & set(formats):
        formats.insert(0, OutputFormat.epub)
    for fmt in set(formats) & ctx.binder.available_formats:
        with console.status(f'Generating {fmt}...'):
            artifact = ctx.binder.make_artifact(
                novel.id,
                novel.title,
                format=fmt,
                user_id=user.id,
                epub=artifacts.get(OutputFormat.epub),
            )
        if artifact.is_available:
            artifacts[fmt] = artifact
            file = ctx.files.resolve(artifact.output_file)
            size = format_size(artifact.file_size or 0)
            print(f'Generated [b]{file}[/b] ({size})')
        else:
            print(f'[red]Failed to generate [b]{fmt.value}[/b][/red]')

    if not non_interactive and _prompt_open_artifact_folder():
        cover_file = ctx.files.resolve(novel.cover_file)
        open_folder(cover_file.parent / 'artifacts')


def _prompt_url() -> str:
    print('[i]The URL must start with [cyan]http[/cyan] or [cyan]https[/cyan].[/i]')
    return questionary.text(
        "Novel page URL:",
        qmark="🌐",
        validate=validate_url,
    ).ask()


def _prompt_format_selection() -> List[OutputFormat]:
    defaults = [OutputFormat.epub, OutputFormat.json]
    return questionary.checkbox(
        "Select novel output formats:",
        choices=[
            questionary.Choice(
                value=fmt,
                title=fmt.value,
                checked=fmt in defaults
            )
            for fmt in list(OutputFormat)
            if fmt in ctx.binder.available_formats
        ],
    ).ask()


def _prompt_chapter_selection(novel: Novel) -> List[str]:
    return []


def _prompt_open_artifact_folder() -> bool:
    return questionary.confirm(
        "Open the artifact folder?",
        default=True,
    ).ask()
