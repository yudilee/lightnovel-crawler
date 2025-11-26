from pathlib import Path

from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from ...context import ctx
from ...exceptions import ServerErrors


class StaticFilesGuard(BaseHTTPMiddleware):
    def __init__(self, app, prefix: str = '/static') -> None:
        self.prefix = prefix
        self.prefix_len = len(self.prefix) + 1
        super().__init__(app)

    async def dispatch(self, request, call_next):
        path = request.url.path
        if not path.startswith(self.prefix):
            return await call_next(request)

        if not ctx.files.exists(path[self.prefix_len:]):
            return ServerErrors.no_such_file.to_response()

        token = request.query_params.get('token')
        if not token:
            return ServerErrors.forbidden.to_response()

        user = ctx.users.verify_token(token, [])
        if not user.is_active:
            return ServerErrors.inactive_user.to_response()

        return await call_next(request)


class CustomStaticFiles(StaticFiles):
    def __init__(self) -> None:
        super().__init__(
            directory=ctx.config.app.output_path
        )

    async def get_response(self, path, scope):
        resp = await super().get_response(path, scope)

        if resp.status_code < 400:
            if '/artifacts/' in path:
                filename = Path(path).name
                resp.headers["content-disposition"] = f'attachment; filename="{filename}"'
                if path.endswith(".epub"):
                    resp.media_type = "application/epub+zip"
                    resp.headers["content-type"] = "application/epub+zip"

        return resp
