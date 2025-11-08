from typing import List, Optional

from fastapi import APIRouter, Form, Path, Query, Security
from pydantic import HttpUrl

from ...context import ctx
from ...dao import Job
from ...dao.enums import JobPriority, JobStatus, JobType, OutputFormat
from ...exceptions import ServerErrors
from ..models.pagination import Paginated
from ..models.user import User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get("s", summary='Returns a list of jobs')
def list_jobs(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    type: Optional[JobType] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    status: Optional[JobStatus] = Query(default=None),
    priority: Optional[JobPriority] = Query(default=None),
    parent_job_id: Optional[str] = Query(default=None),
    is_done: Optional[bool] = Query(default=None),
) -> Paginated[Job]:
    return ctx.jobs.list(
        limit=limit,
        offset=offset,
        user_id=user_id,
        job_type=type,
        status=status,
        is_done=is_done,
        priority=priority,
        parent_job_id=parent_job_id,
    )


@router.delete("/{job_id}", summary='Deletes a job')
def delete_job(
    user: User = Security(ensure_user),
    job_id: str = Path(),
) -> bool:
    ctx.jobs.delete(user, job_id)
    return True


@router.get("/{job_id}", summary='Gets job details')
def get_job(
    job_id: str = Path(),
) -> Job:
    return ctx.jobs.get(job_id)


@router.post("/{job_id}/cancel", summary='Cancel a job')
def cancel_job(
    user: User = Security(ensure_user),
    job_id: str = Path(),
) -> bool:
    ctx.jobs.cancel(user, job_id)
    return True


@router.post("/create/fetch-novel", summary='Create a job to fetch novel details')
def fetch_novel(
    user: User = Security(ensure_user),
    url: HttpUrl = Form(description='The novel page url'),
    full: bool = Form(default=False, description='To fetch all contents')
) -> Job:
    return ctx.jobs.fetch_novel(user, url.encoded_string(), full=full)


@router.post("/create/fetch-volumes", summary='Create a job to fetch all chapter contents for the volumes')
def fetch_volumes(
    user: User = Security(ensure_user),
    volumes: List[str] = Form(description='List of volume ids to fetch'),
) -> Job:
    if not volumes:
        raise ServerErrors.no_volumes_to_download
    if len(volumes) == 1:
        return ctx.jobs.fetch_volume(user, volumes[1])
    return ctx.jobs.fetch_many_volumes(user, *volumes)


@router.post("/create/fetch-chapters", summary='Create a job to fetch chapter contents')
def fetch_chapters(
    user: User = Security(ensure_user),
    chapters: List[str] = Form(description='List of chapter ids to fetch'),
) -> Job:
    if not chapters:
        raise ServerErrors.no_chapters_to_download
    if len(chapters) == 1:
        return ctx.jobs.fetch_chapter(user, chapters[1])
    return ctx.jobs.fetch_many_chapters(user, *chapters)


@router.post("/create/fetch-images", summary='Create a job to fetch chapter images')
def fetch_images(
    user: User = Security(ensure_user),
    images: List[str] = Form(description='List of image ids to fetch'),
) -> Job:
    if not images:
        raise ServerErrors.no_images_to_download
    if len(images) == 1:
        return ctx.jobs.fetch_image(user, images[1])
    return ctx.jobs.fetch_many_images(user, *images)


@router.post("/create/make-artifacts", summary='Create a job to make novel artifacts')
def make_artifacts(
    user: User = Security(ensure_user),
    novel_id: str = Form(description='The novel id'),
    formats: List[OutputFormat] = Form(description='The novel id'),
) -> Job:
    if not formats:
        raise ServerErrors.no_artifacts_to_create
    if len(formats) == 1:
        return ctx.jobs.make_artifact(user, novel_id, formats[1])
    return ctx.jobs.make_many_artifacts(user, novel_id, *formats)
