from typing import Any, Dict

from pydantic import computed_field
from sqlmodel import JSON, Column, Field

from ..context import ctx
from ._base import BaseTable


class ChapterImage(BaseTable, table=True):
    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE'
    )
    chapter_id: str = Field(
        foreign_key="chapter.id",
        ondelete='CASCADE'
    )

    url: str = Field(
        index=True,
        description="Image URL"
    )
    crawled: bool = Field(
        index=True,
        default=False,
        description="Whether the image has been downloaded"
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )

    @computed_field  # type:ignore
    @property
    def image_file(self) -> str:
        '''Image file path'''
        return f"novels/{self.novel_id}/images/{self.id}.jpg"

    @computed_field  # type:ignore
    @property
    def is_available(self) -> bool:
        '''Image file is available'''
        return ctx.files.exists(self.image_file)
