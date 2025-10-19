import typer

from ...context import ctx

app = typer.Typer(
    help='Manage sources.',
)


@app.callback(
    invoke_without_command=True,
)
def sources(context: typer.Context):
    if context.invoked_subcommand is None:
        typer.echo(context.get_help())
    else:
        ctx.sources.ensure_load()
