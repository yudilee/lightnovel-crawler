from typing import Optional

from sqlmodel import BigInteger, Field, SQLModel

from ..utils.time_utils import current_timestamp
from ._base import BaseTable
from .enums import UserRole, UserTier


class User(BaseTable, table=True):
    __tablename__ = 'users'  # type: ignore

    password: str = Field(
        description="Hashed password",
        exclude=True
    )
    email: str = Field(
        unique=True,
        index=True,
        description="User Email"
    )
    name: Optional[str] = Field(
        default=None,
        description="Full name"
    )
    role: UserRole = Field(
        default=UserRole.USER,
        description="User role"
    )
    tier: UserTier = Field(
        default=UserTier.BASIC,
        description="User tier"
    )
    is_active: bool = Field(
        default=True,
        description="Active status"
    )


class VerifiedEmail(SQLModel, table=True):
    email: str = Field(
        primary_key=True,
        description="User Email"
    )
    created_at: int = Field(
        sa_type=BigInteger,
        default_factory=current_timestamp
    )
