from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from .commands.crawl import app as crawl
from .commands.discord import app as discord
from .commands.search import app as search
from .commands.server import app as server
from .commands.sources import app as sources
from .commands.telegram import app as telegram
from .commands.version import app as version
from .context import AppContext

# My application context
ctx = AppContext()

# Define typer
app = typer.Typer(
    context_settings={
        # "auto_envvar_prefix": 'LNC',
        "help_option_names": ["-h", "--help"],
    }
)

# Register subcommands
app.add_typer(version)
app.add_typer(crawl)
app.add_typer(search)
app.add_typer(server)
app.add_typer(discord)
app.add_typer(telegram)
app.add_typer(sources, name='sources')


# Define main command
@app.callback(
    invoke_without_command=True,
)
def main(
    context: typer.Context,
    log_level: Annotated[
        int,
        typer.Option(
            "--verbose", "-l",
            help="Log levels: -l = warn, -ll = info, -lll = debug",
            show_default=False,
            count=True,
            metavar="",
        )
    ] = 0,
    config: Annotated[
        Optional[Path],
        typer.Option(
            "--config", "-c",
            help="Config file",
            show_default=False,
            file_okay=True,
        )
    ] = None,
):
    # set context object
    context.obj = ctx
    context.call_on_close(ctx.cleanup)

    # setup logger
    ctx.logger.setup(log_level)

    # setup config
    ctx.config.load(config)

    # bootstrap database
    ctx.db.bootstrap()
    ctx.sources.prepare()

    # show help if no args
    if context.invoked_subcommand is None:
        if ctx.logger.is_info:
            context.fail('Missing command')
        else:
            typer.echo(context.get_help())
