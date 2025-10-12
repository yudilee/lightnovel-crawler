import typer

app = typer.Typer()


@app.command(help='Crawl from novel page URL.')
def crawl():
    pass
