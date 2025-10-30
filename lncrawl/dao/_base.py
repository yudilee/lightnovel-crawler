import uuid
from typing import Any, Dict

from sqlalchemy import event
from sqlmodel import JSON, BigInteger, Field, SQLModel

from ..utils.time_utils import current_timestamp


def generate_uuid():
    return uuid.uuid4().hex


class BaseTable(SQLModel):
    id: str = Field(
        default_factory=generate_uuid,
        primary_key=True,
        description="ID"
    )
    created_at: int = Field(
        default_factory=current_timestamp,
        sa_type=BigInteger
    )
    updated_at: int = Field(
        default_factory=current_timestamp,
        sa_type=BigInteger
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSON,
        description="Additional metadata",
    )


@event.listens_for(BaseTable, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: BaseTable):
    target.updated_at = current_timestamp()
