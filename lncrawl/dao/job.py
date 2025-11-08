from typing import Optional

from pydantic import computed_field
from sqlmodel import BigInteger, Boolean, Field, Index, asc, desc

from ._base import BaseTable
from .enums import JobPriority, JobStatus, JobType


class Job(BaseTable, table=True):
    __tablename__ = 'jobs'  # type: ignore
    __table_args__ = (
        Index("ix_job_is_done", 'id', 'is_done'),
        Index("ix_job_parent_job_id", 'parent_job_id'),
        Index("ix_job_user_parent_id", 'user_id', 'parent_job_id'),
        Index("ix_job_pending_order", 'is_done', desc('priority'), asc('created_at')),
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
    def progress(self) -> int:
        '''Progress percetage (value is between 0 to 100)'''
        return (100 * self.done) // self.total

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
