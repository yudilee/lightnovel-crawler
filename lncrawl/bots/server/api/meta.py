from typing import List

from fastapi import APIRouter, Depends

from ....context import AppContext
from ..models.meta import SupportedSource

# The root router
router = APIRouter()


@router.get("/supported-sources", summary='Returns a list of supported sources')
def list_supported_sources(ctx: AppContext = Depends()) -> List[SupportedSource]:
    return ctx.metadata.list_supported_sources()
