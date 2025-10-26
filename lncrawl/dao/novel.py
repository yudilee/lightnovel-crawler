from typing import Any, Dict, List, Optional

from sqlalchemy import CHAR
from sqlmodel import JSON, Column, Field

from ._base import BaseTable


class Novel(BaseTable, table=True):
    domain: str = Field(
        index=True,
        description="Domain name of the source website"
    )
    url: str = Field(
        unique=True,
        index=True,
        description="Full URL of the novel main page"
    )

    title: str = Field(
        description="Title of the novel"
    )
    authors: Optional[str] = Field(
        default=None,
        description="Comma-separated list of authors"
    )
    synopsis: Optional[str] = Field(
        default=None,
        description="Brief synopsis or novel description"
    )
    tags: List[str] = Field(
        default=[],
        sa_column=Column(JSON),
        description="List of genre or thematic tags"
    )

    cover_url: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Cover image URL",
    )
    cover_file: Optional[str] = Field(
        default=None,
        exclude=True,
        description="Cover image file path",
    )

    mtl: bool = Field(
        default=False,
        description="True if content is machine-translated"
    )
    rtl: bool = Field(
        default=False,
        description="True if text reads right-to-left (e.g. Arabic, Hebrew)"
    )
    manga: bool = Field(
        default=False,
        description="True if this entry is a manga/manhua/comic"
    )
    language: Optional[str] = Field(
        default=None,
        sa_column=Column(CHAR(2)),
        description="ISO 639-1 two-letter language code (e.g. 'en', 'ja', 'zh')",
    )

    volume_count: int = Field(
        default=0,
        description="Number of available volumes",
    )
    chapter_count: int = Field(
        default=0,
        description="Number of available chapters",
    )

    extra: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional metadata"
    )
