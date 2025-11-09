from typing import Optional

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import Artifact
from ...dao.enums import OutputFormat
from ..models.pagination import Paginated
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get(
    "s",
    summary='Returns a list of artifacts',
    dependencies=[Security(ensure_user)],
)
def list_artifacts(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    job_id: Optional[str] = Query(default=None),
    user_id: Optional[str] = Query(default=None),
    novel_id: Optional[str] = Query(default=None),
    format: Optional[OutputFormat] = Query(default=None),
) -> Paginated[Artifact]:
    return ctx.artifacts.list(
        limit=limit,
        offset=offset,
        user_id=user_id,
        job_id=job_id,
        format=format,
        novel_id=novel_id,
    )


@router.get(
    "/{artifact_id}",
    summary='Returns a artifact',
    dependencies=[Security(ensure_user)],
)
def get_artifact(
    artifact_id: str = Path(),
) -> Artifact:
    return ctx.artifacts.get(artifact_id)


@router.get(
    "/latest",
    summary='Returns the latest artifact',
    dependencies=[Security(ensure_user)],
)
def get_latest(
    novel_id: str = Query(),
    format: OutputFormat = Query(),
) -> Optional[Artifact]:
    return ctx.artifacts.get_latest(novel_id, format)
