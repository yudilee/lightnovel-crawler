import typer

app = typer.Typer(
    help='Manage sources.',
)


@app.callback(
    invoke_without_command=True,
)
def sources(context: typer.Context):
    if context.invoked_subcommand is None:
        typer.echo(context.get_help())


@app.command("list", help="List available sources.")
def list_all():
    pass


@app.command("add", help="Create a new source file.")
def create_source():
    pass


@app.command("view", help="Inspect a source.")
def view_source():
    pass


@app.command("import", help="Import a source file.")
def import_source():
    pass
