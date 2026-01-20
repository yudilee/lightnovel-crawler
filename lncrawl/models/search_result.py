from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    info: str = ""

    class Config:
        extra = "allow"


class CombinedSearchResult(BaseModel):
    id: str
    title: str
    novels: List[SearchResult] = Field(default_factory=list)

    class Config:
        extra = "allow"
