from typing import Optional

from pydantic import computed_field
from sqlmodel import BigInteger, Boolean, Field, Index

from ._base import BaseTable
from .enums import JobPriority, JobStatus, JobType


class Job(BaseTable, table=True):
    __tablename__ = 'jobs'  # type: ignore
    __table_args__ = (
        Index("ix_job_is_done", 'id', 'is_done'),
        Index("ix_job_parent_job_id", 'parent_job_id'),
    )

    user_id: str = Field(
        foreign_key="users.id",
        ondelete='CASCADE'
    )
    parent_job_id: Optional[str] = Field(
        default=None,
        foreign_key="jobs.id",
        ondelete='CASCADE',
        nullable=True,
    )
    depends_on: Optional[str] = Field(
        default=None,
        foreign_key="jobs.id",
        ondelete='CASCADE',
        nullable=True,
    )

    type: JobType = Field(
        description="The job type",
    )
    priority: JobPriority = Field(
        default=JobPriority.LOW,
        description="The job priority"
    )
    status: JobStatus = Field(
        default=JobStatus.PENDING,
        description="Current status"
    )
    is_done: bool = Field(
        default=False,
        sa_type=Boolean,
        description="Whether the job has completed"
    )
    error: Optional[str] = Field(
        default=None,
        description='Error state in case of failure'
    )
    started_at: Optional[int] = Field(
        default=None,
        sa_type=BigInteger,
        description="Job start time (UNIX ms)"
    )
    finished_at: Optional[int] = Field(
        default=None,
        sa_type=BigInteger,
        description="Job finish time (UNIX ms)"
    )

    done: int = Field(
        default=0,
        description="Currently completed items"
    )
    total: int = Field(
        default=1,
        description="Total items to complete"
    )

    @computed_field  # type: ignore[misc]
    @property
    def is_running(self) -> int:
        '''Whether the job is currently running'''
        return self.status == JobStatus.RUNNING

    @computed_field  # type: ignore[misc]
    @property
    def is_pending(self) -> int:
        '''Whether the job is currently pending'''
        return self.status == JobStatus.PENDING

    @computed_field  # type: ignore[misc]
    @property
    def progress(self) -> int:
        '''Progress percetage (value is between 0 to 100)'''
        return (100 * self.done) // self.total

    @computed_field  # type: ignore[misc]
    @property
    def job_title(self) -> str:
        if (
            self.type == JobType.NOVEL
            or self.type == JobType.FULL_NOVEL
        ):
            return self.extra['url']

        if (
            self.type == JobType.NOVEL_BATCH
            or self.type == JobType.FULL_NOVEL_BATCH
        ):
            urls = self.extra['urls']
            if len(urls) == 1:
                return urls[0]
            else:
                return f'{urls[0]} & {len(urls) - 1} more'

        novel_title = self.extra.get('novel_title')
        if novel_title:
            novel_title += ' · '
        else:
            novel_title = 'Fetch '

        if self.type == JobType.VOLUME:
            volume_serial = self.extra.get('volume_serial') or ''
            if volume_serial:
                return f'{novel_title}Volume {volume_serial}'
            else:
                return f'{novel_title}Volume'

        if self.type == JobType.VOLUME_BATCH:
            ids = self.extra.get('volume_ids') or []
            return f'{novel_title}{len(ids)} Volumes'

        if self.type == JobType.CHAPTER:
            chapter_serial = self.extra.get('chapter_serial')
            if chapter_serial:
                return f'{novel_title}Chapter {chapter_serial}'
            else:
                return f'{novel_title}Chapter'
        if self.type == JobType.CHAPTER_BATCH:
            ids = self.extra.get('chapter_ids') or []
            return f'{novel_title}{len(ids)} Chapters'

        if self.type == JobType.IMAGE:
            return self.extra.get('url') or f'{novel_title}1 Image'

        if self.type == JobType.IMAGE_BATCH:
            ids = self.extra.get('image_ids') or []
            return f'{novel_title}{len(ids)} Images'

        if self.type == JobType.ARTIFACT:
            format = self.extra.get('format') or 'Artifact'
            return f'{novel_title}{format}'

        if self.type == JobType.ARTIFACT_BATCH:
            formats = self.extra.get('formats') or []
            if len(formats) <= 2:
                return f"{novel_title}{', '.join(formats)}"
            else:
                return f"{novel_title}{', '.join(formats[:2])} & {len(formats) - 2} more"

        return f'Job {self.id}'
