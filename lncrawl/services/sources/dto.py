from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional, Type

from pydantic import BaseModel, ConfigDict, Field

from ...context import ctx
from ...core.crawler import Crawler


class AppInfo(BaseModel):
    windows: str = Field(..., description="Windows app download URL")
    linux: str = Field(..., description="Linux app download URL")
    version: str = Field(..., description="Application version")
    home: Optional[str] = Field(None, description="Homepage URL or None")
    pypi: str = Field(..., description="PyPI release URL")


class CrawlerInfo(BaseModel):
    id: str
    md5: str
    url: str
    version: int
    file_path: str
    base_urls: List[str]
    has_mtl: bool
    has_manga: bool
    can_search: bool
    can_login: bool
    total_commits: int = 1
    contributors: List[str] = []

    @cached_property
    def user_file(self) -> Path:
        path = ctx.config.crawler.local_sources.parent
        return (path / self.file_path).absolute()

    @cached_property
    def local_file(self) -> Path:
        path = ctx.config.crawler.local_sources.parent
        return (path / self.file_path).absolute()


class CrawlerIndex(BaseModel):
    v: int = Field(..., description="Version or build number")
    app: AppInfo
    rejected: Dict[str, str] = Field(default_factory=dict)
    supported: Dict[str, str] = Field(default_factory=dict)
    crawlers: Dict[str, CrawlerInfo] = Field(default_factory=dict)


class SourceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str = Field(description='Source base url')
    domain: str = Field(description='Domain name')
    version: int = Field(description='Version number')
    has_manga: bool = Field(default=False)
    has_mtl: bool = Field(default=False)
    language: str = Field(default='en', description='2 letter language code')
    is_disabled: bool = Field(default=False)
    disable_reason: Optional[str] = Field(default=None)
    can_search: bool = Field(default=False)
    can_login: bool = Field(default=False)
    total_commits: int = Field(default=0)
    contributors: List[str] = Field(default=[])

    info: CrawlerInfo = Field(..., exclude=True)
    crawler: Type[Crawler] = Field(..., exclude=True)

    @cached_property
    def current_file(self):
        return Path(getattr(self.crawler, '__file__'))

    def __hash__(self) -> int:
        return hash(self.info.id)
