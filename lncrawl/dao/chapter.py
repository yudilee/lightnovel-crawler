from typing import Any, Dict, List, Optional

from sqlmodel import JSON, Column, Field, UniqueConstraint

from ._base import BaseTable


class Chapter(BaseTable, table=True):
    __table_args__ = (
        UniqueConstraint("novel_id", "serial"),
    )

    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE'
    )
    serial: int = Field(
        index=True,
        description="Serial number of the volume",
    )
    volume_id: Optional[str] = Field(
        default=None,
        foreign_key="volume.id",
        ondelete='SET NULL',
    )

    url: str = Field(
        index=True,
        description="Full URL of the chapter content page"
    )
    title: str = Field(
        description="Title of the chapter"
    )

    crawled: bool = Field(
        default=False,
        description="Whether the content has been crawled"
    )
    content_file: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Content file path"
    )
    images: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Related image files"
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
