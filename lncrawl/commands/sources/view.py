from datetime import datetime
import questionary
import typer
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ...context import ctx
from .app import app


@app.command("view", help="Inspect a source.")
def view_one(
    query: str = typer.Argument(
        help="The crawler name, url, or file path to find exact source.",
    ),
):
    # Find unique source
    sources = ctx.sources.list(query, include_rejected=True)
    items = list(set([item for _, item in sources]))

    if not items:
        print('[red]No crawler found.[/red]')
        return

    if len(items) > 5:
        print('[i]Please modify your query to find a unique crawler![/i]')
        print(f'[red]{len(items)} crawlers found.[/red]')
        return

    if len(items) != 1:
        item = questionary.select(
            'Choose a crawler',
            choices=[
                questionary.Choice(url, value=item)
                for item in items
                for url in item.info.base_urls
            ]
        ).ask()
        if not item:
            return
    else:
        item = items[0]

    # Display source details
    table = Table(show_header=False, show_lines=False, box=None)
    table.add_column('Field', style='green', justify='right', no_wrap=True)
    table.add_column('Value', overflow='fold')

    table.add_row(
        'Supports',
        Text(
            '\n'.join([
                f'- {url}'
                for url in item.info.base_urls
            ]),
            style='cyan',
        )
    )
    table.add_row(
        'Features',
        '\n'.join((filter(None, [
            '- Machine Translation' if item.info.has_mtl else '',
            '- Manga' if item.info.has_manga else '',
            '- Search' if item.info.can_search else '',
            '- Login' if item.info.can_login else '',
        ])))
    )
    table.add_row(
        'Last Update',
        datetime.fromtimestamp(item.info.version).strftime('%c')
    )
    table.add_row(
        'Contributors',
        ', '.join(item.info.contributors)
    )
    table.add_row(
        'Source file',
        Text(str(item.current_file), style='cyan')
    )

    panel = Panel(
        table,
        title=Text(item.crawler.__name__, style='bold yellow'),
        title_align='left',
    )

    print(panel)
