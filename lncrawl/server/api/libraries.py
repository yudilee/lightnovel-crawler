from typing import List

from fastapi import APIRouter, Path, Query, Security

from ...context import ctx
from ...dao import Library, Novel, User
from ...server.models.library import (LibraryAddNovelRequest, LibraryItem,
                                      LibraryCreateRequest, LibrarySummary,
                                      LibraryUpdateRequest)
from ...server.models.pagination import Paginated
from ..security import ensure_admin, ensure_user

router = APIRouter()


@router.get(
    "/all",
    summary="Returns all libraries (admin only)",
    dependencies=[Security(ensure_admin)],
)
def list_all_libraries(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[LibrarySummary]:
    return ctx.libraries.list(offset, limit)


@router.get(
    "/public",
    summary="Returns public libraries",
    dependencies=[Security(ensure_user)],
)
def list_public_libraries(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[LibrarySummary]:
    return ctx.libraries.list(offset, limit, public_only=True)


@router.get(
    "/my",
    summary="Returns current user's libraries",
)
def list_my_libraries(
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    user: User = Security(ensure_user),
) -> Paginated[LibrarySummary]:
    return ctx.libraries.list(offset, limit, user_id=user.id)


@router.get(
    "/my/list",
    summary="Get library name suggestions",
)
def all_my_libraries(user: User = Security(ensure_user)) -> List[LibraryItem]:
    return ctx.libraries.list_all(user.id)


@router.post(
    "",
    summary="Create a new library",
)
def create_library(
    payload: LibraryCreateRequest,
    user: User = Security(ensure_user),
) -> Library:
    return ctx.libraries.create(
        user_id=user.id,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
    )


@router.get(
    "/{library_id}",
    summary="Get library details",
)
def get_library(
    library_id: str = Path(),
    user: User = Security(ensure_user),
) -> Library:
    return ctx.libraries.get(library_id, user)


@router.patch(
    "/{library_id}",
    summary="Update a library",
)
def update_library(
    payload: LibraryUpdateRequest,
    library_id: str = Path(),
    user: User = Security(ensure_user),
) -> Library:
    return ctx.libraries.update(
        library_id=library_id,
        user=user,
        name=payload.name,
        description=payload.description,
        is_public=payload.is_public,
    )


@router.delete(
    "/{library_id}",
    summary="Delete a library",
)
def delete_library(
    library_id: str = Path(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.libraries.delete(library_id, user)


@router.get(
    "/{library_id}/novels",
    summary="List novels in library",
)
def list_library_novels(
    library_id: str = Path(),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
    user: User = Security(ensure_user),
) -> Paginated[Novel]:
    return ctx.libraries.list_novels(
        library_id=library_id,
        user=user,
        offset=offset,
        limit=limit,
    )


@router.post(
    "/{library_id}/novels",
    summary="Add a novel to library",
)
def add_novel_to_library(
    payload: LibraryAddNovelRequest,
    library_id: str = Path(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.libraries.add_novel(library_id, user, payload.novel_id)


@router.delete(
    "/{library_id}/novels/{novel_id}",
    summary="Remove a novel from library",
)
def remove_novel_from_library(
    library_id: str = Path(),
    novel_id: str = Path(),
    user: User = Security(ensure_user),
) -> bool:
    return ctx.libraries.remove_novel(library_id, user, novel_id)
