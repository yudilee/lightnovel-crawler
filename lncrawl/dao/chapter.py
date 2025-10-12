from typing import Any, Dict, Optional

from sqlmodel import JSON, BigInteger, Column, Field

from ._base import BaseTable


class Chapter(BaseTable, table=True):
    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE'
    )
    url: str = Field(
        unique=True,
        index=True,
        description="Full URL of the chapter content page"
    )

    volume: Optional[str] = Field(
        default=None,
        description="Name of the volume if available"
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the chapter"
    )
    content: Optional[str] = Field(
        default=None,
        description="Content of the chapter"
    )
    size: int = Field(
        default=0,
        index=True,
        sa_type=BigInteger,
        description="Content size in bytes"
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
