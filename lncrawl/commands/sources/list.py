from typing import Optional

import typer
from rich import print
from rich.table import Table
from rich.text import Text

from ...assets.icons import Icons
from ...context import ctx
from .app import app


@app.command("list", help="List available sources.")
def list_all(
    query: Optional[str] = typer.Option(
        None,
        "-q",
        "--query",
        help="Filter sources by keyword in the URL.",
    ),
    can_search: Optional[bool] = typer.Option(
        None,
        "-s",
        "--can-search",
        help="Show only sources that support novel search.",
    ),
    can_login: Optional[bool] = typer.Option(
        None,
        "-l",
        "--can-login",
        help="Show only sources that support login.",
    ),
    has_mtl: Optional[bool] = typer.Option(
        None,
        "-b",
        "--mtl",
        help="Show only machine-translated sources.",
    ),
    has_manga: Optional[bool] = typer.Option(
        None,
        '-m',
        "--manga",
        help="Show only manga/manhua sources.",
    ),
    include_rejected: bool = typer.Option(
        False,
        "--with-rejected",
        help="Include rejected or disabled sources in the list.",
    ),
):
    """
    Display a list of supported crawler sources.
    Filters can be combined to narrow down the results.
    """
    sources = ctx.sources.list(
        query=query,
        include_rejected=include_rejected,
        can_search=can_search,
        can_login=can_login,
        has_mtl=has_mtl,
        has_manga=has_manga
    )

    if not sources:
        print('[red]No sources found.[/red]')
        return

    table = Table(title='List supported sources')
    table.add_column('#', style='cyan', no_wrap=True, justify='right')
    table.add_column('URL', overflow='fold')
    table.add_column('Search', justify='center')
    table.add_column('Login', justify='center')
    table.add_column('Manga', justify='center')
    table.add_column('MTL', justify='center', min_width=5)

    for i, (url, item) in enumerate(sources):
        yes_no = {
            True: Icons.CHECK,
            False: '',
        }
        url = Text(url, style='blue')
        if query:
            url.highlight_regex(query, style='yellow')
        table.add_row(
            str(i),
            url,
            yes_no[item.info.can_search],
            yes_no[item.info.can_login],
            yes_no[item.info.has_manga],
            yes_no[item.info.has_mtl],
        )

    print(table)
