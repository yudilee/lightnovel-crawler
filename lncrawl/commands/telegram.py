import typer

app = typer.Typer()


@app.command(help='Run Telegram bot.')
def telegram():
    raise NotImplementedError()
