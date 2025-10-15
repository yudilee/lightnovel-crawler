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
    can_logout: bool
    total_commits: int = 1
    contributors: List[str] = []

    @cached_property
    def user_file(self) -> Path:
        path = ctx.config.crawler.user_index_file.parent.parent
        return (path / self.file_path).absolute()

    @cached_property
    def local_file(self) -> Path:
        path = ctx.config.crawler.local_index_file.parent.parent
        return (path / self.file_path).absolute()


class CrawlerIndex(BaseModel):
    v: int = Field(..., description="Version or build number")
    app: AppInfo
    rejected: Dict[str, str] = Field(default_factory=dict)
    supported: Dict[str, str] = Field(default_factory=dict)
    crawlers: Dict[str, CrawlerInfo] = Field(default_factory=dict)


class SourceItem(BaseModel):
    model_config = ConfigDict(frozen=True)
    info: CrawlerInfo
    crawler: Type[Crawler]

    @cached_property
    def current_file(self):
        return Path(getattr(self.crawler, '__file__'))

    def __hash__(self) -> int:
        return hash(self.info.id)
