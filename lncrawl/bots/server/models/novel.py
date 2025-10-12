from typing import List, Optional

from pydantic import BaseModel


class NovelChapter(BaseModel):
    id: int
    title: str
    hash: str


class NovelVolume(BaseModel):
    id: int
    title: str
    chapters: List[NovelChapter] = []


class NovelChapterContent(BaseModel):
    id: int
    title: str
    body: str
    volume_id: int
    volume: str
    prev: Optional[NovelChapter] = None
    next: Optional[NovelChapter] = None
