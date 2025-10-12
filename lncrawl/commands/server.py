import typer

app = typer.Typer()


@app.command(help='Run web server.')
def server():
    pass
