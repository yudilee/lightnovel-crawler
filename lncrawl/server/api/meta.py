from typing import Iterable

from fastapi import APIRouter, Depends, Query
from pydantic import HttpUrl
from starlette.responses import FileResponse

from ...context import ctx
from ...utils.url_tools import extract_host
from ..models.meta import SupportedSource
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get(
    "/supported-sources",
    summary='Returns a list of supported sources',
    dependencies=[Depends(ensure_user)],
)
def list_supported_sources() -> Iterable[SupportedSource]:
    for url, item in ctx.sources.list(include_rejected=True):
        domain = extract_host(url)
        yield SupportedSource(
            url=url,
            domain=domain,
            has_mtl=item.info.has_mtl,
            has_manga=item.info.has_manga,
            can_login=item.info.can_login,
            can_search=item.info.can_search,
            is_disabled=(domain in ctx.sources.rejected),
            disable_reason=ctx.sources.rejected.get(domain, ''),
        )


@router.get(
    "/favicon",
    summary='Get favicon of a site',
)
def get_favicon(
    url: HttpUrl = Query(description='URL'),
    token: str = Query(description='Authentication token'),
) -> FileResponse:
    ctx.users.verify_token(token)
    file = ctx.http.favicon(url.encoded_string())
    return FileResponse(
        file,
        filename='favicon.ico',
        media_type='image/x-icon',
        headers={
            "Cache-Control": "public, max-age=31536000, immutable"
        },
    )
