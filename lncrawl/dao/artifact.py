from typing import Optional

from pydantic import computed_field
from sqlmodel import Field

from ..context import ctx
from ._base import BaseTable
from .enums import OutputFormat


class Artifact(BaseTable, table=True):
    __tablename__ = 'artifacts'  # type: ignore

    novel_id: str = Field(
        foreign_key="novels.id",
        ondelete='CASCADE'
    )
    job_id: Optional[str] = Field(
        foreign_key="jobs.id",
        ondelete='SET NULL'
    )
    user_id: Optional[str] = Field(
        foreign_key="users.id",
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

    @computed_field  # type: ignore[misc]
    @property
    def is_available(self) -> bool:
        '''Content file is available'''
        return ctx.files.exists(self.output_file)

    @computed_field  # type: ignore[misc]
    @property
    def file_size(self) -> Optional[int]:
        '''Output file size in bytes'''
        try:
            file = ctx.files.resolve(self.output_file)
            return file.stat().st_size
        except Exception:
            return None
