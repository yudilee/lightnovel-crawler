from fastapi import APIRouter, Body, Security

from ...context import ctx
from ...dao import User
from ...server.models.user import PutNotificationRequest, UpdateRequest
from ..security import ensure_user

# The root router
router = APIRouter()


@router.put(
    "/notifications",
    summary='Save user notification settings',
)
def put_notification_settings(
    user: User = Security(ensure_user),
    body: PutNotificationRequest = Body()
) -> bool:
    request = UpdateRequest(
        extra=dict(
            email_alerts=body.email_alerts
        )
    )
    ctx.users.update(user.id, request)
    return True
