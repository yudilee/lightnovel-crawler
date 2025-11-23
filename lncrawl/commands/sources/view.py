from datetime import datetime

import questionary
import typer
from rich import print
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

    # Display supported urls
    print('[green]:right_arrow: Supports:[/green]', end='')
    if len(item.info.base_urls) > 1:
        print()
        for url in item.info.base_urls:
            print(f'  - [cyan]{url}[/cyan]')
    else:
        print(f' [cyan]{item.info.base_urls[0]}[/cyan]')

    # Display features
    features = []
    if item.info.has_mtl:
        features.append('Machine Translation')
    if item.info.has_manga:
        features.append('Manga')
    if item.info.can_search:
        features.append('Search')
    if item.info.can_login:
        features.append('Login')
    if features:
        print('[green]:right_arrow: Features:[/green]', end='')
        if len(features) > 1:
            print()
            for feature in features:
                print(f'  - {feature}')
        else:
            print(f' {features[0]}')

    # Display version
    print(
        '[green]:right_arrow: Last Update:[/green]',
        datetime.fromtimestamp(item.info.version).strftime(r"%Y %b %d %I:%M:%S %p")
    )

    # Display commit count and contributors
    contribs = ', '.join(item.info.contributors)
    if contribs:
        if item.info.total_commits > 0:
            contribs = f'{item.info.total_commits} commits by {contribs}'
        print(
            '[green]:right_arrow: Contributors:[/green]',
            contribs
        )

    # Display source file
    print(
        '[green]:right_arrow: Source file:[/green]',
        Text(str(item.current_file), style='cyan', no_wrap=True)
    )

    # Display download link
    if item.info.url:
        print(
            '[green]:right_arrow: Download URL:[/green]',
            Text(item.info.url, style='cyan', no_wrap=True)
        )
