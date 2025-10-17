import typer
import uvicorn

from ..context import ctx

app = typer.Typer()


@app.command(help='Run web server.')
def server(
    host: str = typer.Option(
        '0.0.0.0',
        '-h', '--host',
        help='Server host'
    ),
    port: int = typer.Option(
        8080,
        '-p', '--port',
        help='Server port'
    ),
    watch: bool = typer.Option(
        False,
        '-w', '--watch',
        is_flag=True,
        help='Run server in watch mode',
    ),
):
    if watch:
        uvicorn.run(
            "lncrawl.server.app:app",
            workers=1,
            reload=True,
            port=port,
            host=host,
            log_level=ctx.logger.level,
        )
    else:
        from ..server.app import app as server
        uvicorn.run(
            server,
            port=port,
            host=host,
            log_level=ctx.logger.level,
        )
