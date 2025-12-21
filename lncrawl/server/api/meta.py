from typing import List

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import HttpUrl
from starlette.responses import FileResponse

from ...context import ctx
from ...services.sources.dto import SourceItem
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get(
    "/supported-sources",
    summary='Returns a list of supported sources',
    dependencies=[Depends(ensure_user)],
    response_model=List[SourceItem],
)
def list_supported_sources(request: Request):
    etag = str(ctx.sources.version)
    headers = {
        "ETag": etag,
        "Vary": "Accept, If-None-Match, Authorization",
        "Cache-Control": "public, max-age=14400, immutable",
    }

    if_none_match = request.headers.get("if-none-match")
    if if_none_match == etag:
        return Response(status_code=304, headers=headers)

    result = ctx.sources.list(include_rejected=True)
    return JSONResponse(
        content=[item.model_dump() for item in result],
        headers=headers
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
