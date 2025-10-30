from typing import List, Optional

from fastapi import APIRouter, Form, Path, Query, Security
from pydantic import HttpUrl

from ...context import ctx
from ...dao import Job
from ...dao.enums import JobPriority, JobStatus, JobType
from ..models.pagination import Paginated
from ..models.user import User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of jobs')
def list_jobs(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    sort_by: str = Query(default="created_at"),
    order: str = Query(default="desc", regex="^(asc|desc)$"),
    type: Optional[JobType] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    status: Optional[JobStatus] = Query(default=None),
    priority: Optional[JobPriority] = Query(default=None),
) -> Paginated[Job]:
    return ctx.jobs.list(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
        status=status,
        job_type=type,
        priority=priority,
        user_id=user_id,
    )


@router.delete("/{job_id}", summary='Deletes a job')
def delete_job(
    job_id: str = Path(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.jobs.delete(job_id, user)


@router.get("/{job_id}", summary='Gets job details')
def get_job(
    job_id: str = Path(),
) -> Job:
    return ctx.jobs.get(job_id)


@router.post("/{job_id}/cancel", summary='Cancel a job')
def cancel_job(
    job_id: str = Path(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.jobs.cancel(job_id, user)


@router.post("/novel", summary='Creates a job to fetch novel details')
def create_fetch_novel_job(
    user: User = Security(ensure_user),
    url: HttpUrl = Form(description='The novel page url'),
) -> Job:
    return ctx.jobs.fetch_novel(user, url)


@router.post("/full-novel", summary='Creates a job to fetch novel in full with details, chapter contents and images')
def create_fetch_full_novel_job(
    user: User = Security(ensure_user),
    url: HttpUrl = Form(description='The novel page url'),
) -> Job:
    return ctx.jobs.fetch_novel(user, url, full=True)


@router.post("/chapters", summary='Create a job to fetch chapter contents')
def create_fetch_chapter_job(
    user: User = Security(ensure_user),
    chapters: List[str] = Form(description='The chapter ids'),
) -> Job:
    return ctx.jobs.fetch_chapter(user, chapters)
