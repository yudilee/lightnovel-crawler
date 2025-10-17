from typing import Iterable

from fastapi import APIRouter

from ...context import ctx
from ..models.meta import SupportedSource

# The root router
router = APIRouter()


@router.get("/supported-sources", summary='Returns a list of supported sources')
def list_supported_sources() -> Iterable[SupportedSource]:
    return ctx.metadata.list_supported_sources()
