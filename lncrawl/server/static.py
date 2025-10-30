from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from ..context import ctx
from ..exceptions import ServerErrors

app = FastAPI()


@app.middleware("http")
async def static_auth_middleware(request: Request, call_next):
    path = request.url.path[len("/static/"):]
    if not ctx.files.exists(path):
        raise ServerErrors.no_such_file
    token = request.query_params.get('token')
    if not token:
        raise ServerErrors.forbidden
    user = ctx.users.verify_token(token, [])
    if not user.is_active:
        raise ServerErrors.inactive_user
    return await call_next(request)

app.mount(
    "/",
    StaticFiles(
        directory=ctx.config.app.output_path,
        check_dir=False,
        html=False
    ),
    name="static",
)
