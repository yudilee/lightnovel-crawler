from typing import List

from fastapi import APIRouter, Path, Query

from ...context import ctx
from ...dao import Artifact, Chapter, Novel, Volume
from ..models.pagination import Paginated

# The root router
router = APIRouter()


@router.get(
    "s",
    summary='Returns a list of novels',
)
def list_novels(
    search: str = Query(default=''),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[Novel]:
    return ctx.novels.list(
        limit=limit,
        offset=offset,
        search=search.strip(),
    )


@router.get("/{novel_id}", summary='Returns a novel')
def get_novel(
    novel_id: str = Path(),
) -> Novel:
    return ctx.novels.get(novel_id)


@router.get("/{novel_id}/volumes", summary='Gets volumes')
async def get_novel_volumes(
    novel_id: str = Path(),
) -> List[Volume]:
    return ctx.volumes.list(novel_id=novel_id)


@router.get("/{novel_id}/chapters", summary='Gets all chapters')
async def get_novel_chapters(
    novel_id: str = Path(),
) -> List[Chapter]:
    return ctx.chapters.list(novel_id=novel_id)


@router.get("/{novel_id}/artifacts", summary='Gets latest artifacts')
async def get_novel_artifacts(
    novel_id: str = Path(),
) -> List[Artifact]:
    return ctx.artifacts.list_latest(novel_id=novel_id)
