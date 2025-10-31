from typing import Optional

from sqlmodel import Field, SQLModel


class Tag(SQLModel, table=True):
    __tablename__ = 'tags'  # type: ignore

    name: str = Field(
        nullable=False,
        primary_key=True,
        description="Unique tag name"
    )
    description: Optional[str] = Field(
        default=None,
        description="Tag description"
    )
