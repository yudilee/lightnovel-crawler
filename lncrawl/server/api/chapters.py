from typing import List

from fastapi import APIRouter, Path, Security, Query

from ...context import ctx
from ...dao import Chapter, ChapterImage, Job, User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("/{chapter_id}", summary='Returns a chapter details')
def get_chapter(
    chapter_id: str = Path(),
) -> Chapter:
    return ctx.chapters.get(chapter_id)


@router.get("/{chapter_id}/fetch", summary='Create a job to fetch chapter content')
def fetch_chapter(
    user: User = Security(ensure_user),
    chapter_id: str = Path(),
) -> Job:
    return ctx.jobs.fetch_chapter(user, chapter_id)


@router.get("/{chapter_id}/images", summary='Gets list of chapter images')
async def get_chapter_images(
    chapter_id: str = Path(),
    available_only: bool = Query(default=False, description='List only available images')
) -> List[ChapterImage]:
    return ctx.images.list(
        chapter_id=chapter_id,
        is_crawled=available_only,
    )
