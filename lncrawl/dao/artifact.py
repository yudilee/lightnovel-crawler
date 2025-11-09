from typing import Optional

from pydantic import computed_field
from sqlmodel import Field

from ..context import ctx
from ._base import BaseTable
from .enums import OutputFormat


class Artifact(BaseTable, table=True):
    __tablename__ = 'artifacts'  # type: ignore

    novel_id: str = Field(
        index=True,
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
    format: OutputFormat = Field(
        index=True,
        description="The output format of the artifact"
    )
    file_name: str = Field(
        description='Artifact output file name'
    )

    @computed_field  # type: ignore[misc]
    @property
    def output_file(self) -> str:
        '''Artifact file path'''
        return f"novels/{self.novel_id}/artifacts/{self.file_name}"

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
