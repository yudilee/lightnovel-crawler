from fastapi import APIRouter, Depends, Security

from ..security import ensure_admin, ensure_user
from .admin import router as admin
from .artifacts import router as artifact
from .auth import router as auth
from .jobs import router as job
from .meta import router as metadata
from .novels import router as novel
from .users import router as user
from .volumes import router as volume

router = APIRouter()

router.include_router(
    auth,
    prefix='/auth',
    tags=['Auth'],
)

router.include_router(
    user,
    prefix='/user',
    tags=['Users'],
    dependencies=[Depends(ensure_admin)],
)


router.include_router(
    novel,
    prefix='/novel',
    tags=['Novels'],
    dependencies=[Depends(ensure_user)],
)

router.include_router(
    volume,
    prefix='/volume',
    tags=['Volumes'],
    dependencies=[Depends(ensure_user)],
)

router.include_router(
    artifact,
    prefix='/artifact',
    tags=['Artifacts'],
    dependencies=[Depends(ensure_user)],
)

router.include_router(
    metadata,
    prefix='/meta',
    tags=['Metadata'],
    dependencies=[Depends(ensure_user)],
)

router.include_router(
    job,
    prefix='/job',
    tags=['Jobs'],
    dependencies=[Security(ensure_user)],
)

router.include_router(
    admin,
    prefix='/admin',
    tags=['Admin'],
    dependencies=[Depends(ensure_admin)],
)
