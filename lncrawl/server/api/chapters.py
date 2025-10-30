from fastapi import APIRouter, Path, Security

from ...context import ctx
from ...dao import Chapter, Job, User
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
