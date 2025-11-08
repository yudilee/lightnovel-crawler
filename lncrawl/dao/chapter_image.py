from pydantic import computed_field
from sqlmodel import Field, Index

from ..context import ctx
from ._base import BaseTable


class ChapterImage(BaseTable, table=True):
    __tablename__ = 'chapter_images'  # type: ignore
    __table_args__ = (
        Index("ix_chapter_image_chapter", 'chapter_id'),
    )

    novel_id: str = Field(
        foreign_key="novels.id",
        ondelete='CASCADE'
    )
    chapter_id: str = Field(
        foreign_key="chapters.id",
        ondelete='CASCADE'
    )

    url: str = Field(
        description="Image URL"
    )
    is_done: bool = Field(
        default=False,
        description="Whether the image has been downloaded"
    )

    @computed_field  # type: ignore[misc]
    @property
    def image_file(self) -> str:
        '''Image file path'''
        return f"novels/{self.novel_id}/images/{self.id}.jpg"

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        '''Image file is available'''
        return ctx.files.exists(self.image_file)
