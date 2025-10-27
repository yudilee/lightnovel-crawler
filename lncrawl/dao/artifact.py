from typing import Any, Dict, Optional

from pydantic import computed_field
from sqlmodel import JSON, Column, Field

from ..context import ctx
from ._base import BaseTable
from .enums import OutputFormat


class Artifact(BaseTable, table=True):
    novel_id: str = Field(
        foreign_key="novel.id",
        ondelete='CASCADE'
    )
    job_id: Optional[str] = Field(
        foreign_key="job.id",
        ondelete='SET NULL'
    )
    user_id: Optional[str] = Field(
        foreign_key="user.id",
        ondelete='SET NULL'
    )
    output_file: str = Field(
        description="Output file path",
        exclude=True
    )
    format: OutputFormat = Field(
        index=True,
        description="The output format of the artifact"
    )

    extra: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON),
        description="Extra field"
    )

    @computed_field  # type:ignore
    @property
    def is_available(self) -> bool:
        '''Content file is available'''
        return ctx.files.exists(self.output_file)

    @computed_field  # type:ignore
    @property
    def file_size(self) -> Optional[int]:
        '''Output file size in bytes'''
        try:
            file = ctx.files.resolve(self.output_file)
            return file.stat().st_size
        except Exception:
            return None
