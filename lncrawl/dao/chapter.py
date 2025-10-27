from typing import Any, Dict, Optional

from pydantic import computed_field
from sqlmodel import JSON, Column, Field

from ..context import ctx
from ._base import BaseTable


class Chapter(BaseTable, table=True):
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
        index=True,
        default=False,
        description="Whether the content has been crawled"
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )

    @computed_field  # type:ignore
    @property
    def content_file(self) -> str:
        '''Content file path'''
        return f"novels/{self.novel_id}/chapters/{self.serial:06}.zst"

    @computed_field  # type:ignore
    @property
    def is_available(self) -> bool:
        '''Content file is available'''
        return ctx.files.exists(self.content_file)
