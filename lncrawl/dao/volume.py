from sqlmodel import Field, Index, UniqueConstraint

from ._base import BaseTable


class Volume(BaseTable, table=True):
    __table_args__ = (
        UniqueConstraint("novel_id", "serial"),
        Index("ix_volume_novel_id", 'novel_id'),
        Index("ix_volume_novel_serial", 'novel_id', 'serial'),
    )

    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE',
    )
    serial: int = Field(
        description="Serial number of the volume",
    )
    title: str = Field(
        description="Name of the volume",
    )
