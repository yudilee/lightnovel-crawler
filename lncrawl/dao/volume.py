from typing import Any, Dict

from sqlalchemy import UniqueConstraint
from sqlmodel import JSON, Column, Field

from ._base import BaseTable


class Volume(BaseTable, table=True):
    __table_args__ = (
        UniqueConstraint("novel_id", "serial"),
    )

    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE',
    )
    serial: int = Field(
        index=True,
        description="Serial number of the volume",
    )

    title: str = Field(
        description="Name of the volume",
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
