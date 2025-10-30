from typing import Optional

from sqlmodel import BigInteger, Field, Index, SQLModel, UniqueConstraint

from ..utils.time_utils import current_timestamp


class ReadHistory(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("user_id", "chapter_id"),
        Index("ix_read_history_user_created", 'user_id', 'created_at'),
    )

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    created_at: int = Field(
        default_factory=current_timestamp,
        sa_type=BigInteger
    )
    user_id: str = Field(
        foreign_key="user.id",
        ondelete='CASCADE'
    )
    chapter_id: str = Field(
        foreign_key="chapter.id",
        ondelete='CASCADE'
    )
    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE'
    )
    volume_id: Optional[str] = Field(
        default=None,
        foreign_key="volume.id",
        ondelete='SET NULL',
    )
