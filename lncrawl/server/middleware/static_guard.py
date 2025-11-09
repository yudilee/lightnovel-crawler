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
