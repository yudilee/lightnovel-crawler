from typing import Optional

from pydantic import BaseModel, Field

from ...dao import Library


class LibraryOwner(BaseModel):
    id: str = Field(description="Owner user id")
    name: Optional[str] = Field(default=None, description="Owner name")


class LibraryCreateRequest(BaseModel):
    name: str = Field(description="Library name")
    description: Optional[str] = Field(default=None, description="Library description")
    is_public: bool = Field(default=False, description="Is public")


class LibraryUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, description="Library name")
    description: Optional[str] = Field(default=None, description="Library description")
    is_public: Optional[bool] = Field(default=None, description="Is public")


class LibraryAddNovelRequest(BaseModel):
    novel_id: str = Field(description="Novel id to add")


class LibrarySummary(BaseModel):
    library: Library = Field(description="Library info")
    owner: LibraryOwner = Field(description="Library owner")
    novel_count: int = Field(description="Number of novels")
