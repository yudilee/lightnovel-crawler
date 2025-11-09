from fastapi import APIRouter, Body, Path, Query, Security

from ...context import ctx
from ...exceptions import ServerErrors
from ..models.pagination import Paginated
from ..models.user import CreateRequest, UpdateRequest, User
from ..security import ensure_user

# The root router
router = APIRouter()


@router.get('s', summary='Get list of users')
def list_users(
    search: str = Query(default=''),
    offset: int = Query(default=0),
    limit: int = Query(default=20, le=100),
) -> Paginated[User]:
    return ctx.users.list(offset, limit, search)


@router.post('', summary='Create an user')
def create_user(
    body: CreateRequest = Body(
        default=...,
        description='The signup request',
    ),
) -> User:
    return ctx.users.create(body)


@router.get('/{user_id}', summary='Get the user')
def get_user(
    user_id: str = Path(),
) -> User:
    return ctx.users.get(user_id)


@router.put('/{user_id}', summary='Update the user')
def update_user(
    user: User = Security(ensure_user),
    body: UpdateRequest = Body(
        default=...,
        description='The signup request',
    ),
    user_id: str = Path(),
) -> bool:
    if user_id == user.id:
        body.role = None
        body.is_active = None
    ctx.users.update(user_id, body)
    return True


@router.delete('/{user_id}', summary='Delete the user')
def delete_user(
    user: User = Security(ensure_user),
    user_id: str = Path(),
) -> bool:
    if user.id == user_id:
        raise ServerErrors.can_not_delete_self
    ctx.users.remove(user_id)
    return True
