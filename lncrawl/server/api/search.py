from typing import List

from fastapi import APIRouter, Query

from ...context import ctx
from ...models.search_result import CombinedSearchResult

router = APIRouter()


@router.get(
    "/online",
    summary="Search for novels online across multiple sources",
    response_model=List[CombinedSearchResult],
)
def search_online(
    query: str = Query(..., min_length=2, help="Search query string"),
    limit: int = Query(default=10, le=50, help="Maximum number of results"),
    concurrency: int = Query(default=10, le=25, help="Search concurrency"),
):
    return ctx.search.search(
        query=query,
        limit=limit,
        concurrency=concurrency,
    )
