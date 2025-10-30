from typing import List

from fastapi import APIRouter, Path

from ...context import ctx
from ...dao import Chapter, Volume

# The root router
router = APIRouter()


@router.get("/{volume_id}", summary='Returns a volume details')
def get_volume(
    volume_id: str = Path(),
) -> Volume:
    return ctx.volumes.get(volume_id)


@router.get("/{volume_id}/chapters", summary='Gets all chapters')
async def get_volume_chapters(
    volume_id: str = Path(),
) -> List[Chapter]:
    return ctx.chapters.list(volume_id=volume_id)
