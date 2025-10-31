from sqlmodel import Field, LargeBinary

from ._base import BaseTable
from .enums import SecretType


class Secret(BaseTable, table=True):
    __tablename__ = 'secrets'  # type: ignore

    type: SecretType = Field(
        default=SecretType.TEXT,
        description="Secret type"
    )
    name: str = Field(
        index=True,
        nullable=False,
        max_length=255,
        description="Secret name"
    )
    value: bytes = Field(
        exclude=True,
        sa_type=LargeBinary,
        description="Encrypted secret value"
    )
