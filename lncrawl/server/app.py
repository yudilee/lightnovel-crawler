import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse

from ..assets.version import get_version
from ..context import ctx
from ..exceptions import ServerError

app = FastAPI(
    version=get_version(),
    title="Lightnovel Crawler",
    description="Download novels from online sources and generate e-books",
    on_startup=[ctx.setup],
    on_shutdown=[ctx.destroy],
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# Add APIs
try:
    from .api import router as api
    app.include_router(api, prefix='/api')
except ImportError:
    traceback.print_exc()

# Add frontend
web_dir = (Path(__file__).parent / 'web').absolute()
if web_dir.is_dir():
    @app.get("/{fallback:path}", include_in_schema=False)
    async def serve_static(fallback: str):
        target_file = web_dir.joinpath(fallback)
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(web_dir / "index.html")


# Add exception handlers
@app.exception_handler(ServerError)
async def global_client_error_handler(req: Request, err: ServerError):
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
        headers=err.headers,
    )


@app.exception_handler(HTTPException)
async def global_http_exception_handler(req: Request, err: HTTPException):
    traceback.print_exception(err)
    return JSONResponse(
        status_code=err.status_code,
        content={"detail": err.detail},
        headers=err.headers,
    )


@app.exception_handler(Exception)
async def global_exception_handler(req: Request, err: Exception):
    traceback.print_exception(err)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )
