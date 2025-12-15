import sqlmodel as sa
from typing import Optional

from ._base import BaseTable


class Library(BaseTable, table=True):
    __tablename__ = "libraries"  # type: ignore

    user_id: str = sa.Field(
        foreign_key="users.id",
        description="Owner user id",
        index=True,
        ondelete="CASCADE",
    )

    name: str = sa.Field(
        description="Library name",
        index=True,
    )
    description: Optional[str] = sa.Field(
        default=None,
        description="Library description"
    )
    is_public: bool = sa.Field(
        default=False,
        description="Is library visible to everyone"
    )


class LibraryNovel(sa.SQLModel, table=True):
    __tablename__ = "library_novels"  # type: ignore
    __table_args__ = (
        sa.UniqueConstraint("library_id", "novel_id"),
    )

    library_id: str = sa.Field(
        foreign_key="libraries.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Library id",
    )
    novel_id: str = sa.Field(
        foreign_key="novels.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Novel id",
    )
