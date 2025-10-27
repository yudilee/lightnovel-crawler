from typing import Any, Dict, Optional

from sqlmodel import JSON, Column, Field

from ._base import BaseTable
from .enums import UserRole, UserTier


class User(BaseTable, table=True):
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
    is_verified: bool = Field(
        default=True,
        description="Verification status"
    )

    extra: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON),
        description="Extra field"
    )
