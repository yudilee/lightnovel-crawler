from typing import Iterable

from fastapi import APIRouter

from ...context import ctx
from ...utils.url_tools import extract_host
from ..models.meta import SupportedSource

# The root router
router = APIRouter()


@router.get("/supported-sources", summary='Returns a list of supported sources')
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
