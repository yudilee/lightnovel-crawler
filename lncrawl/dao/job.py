from typing import Optional

from pydantic import computed_field
from sqlalchemy import event
from sqlmodel import BigInteger, Field

from ..utils.time_utils import current_timestamp
from ._base import BaseTable
from .enums import JobPriority, JobStatus, JobType


class Job(BaseTable, table=True):
    user_id: str = Field(
        foreign_key="user.id",
        ondelete='CASCADE'
    )
    parent_job_id: Optional[str] = Field(
        default=None,
        foreign_key="job.id",
        ondelete='CASCADE',
        nullable=True,
    )

    type: JobType = Field(
        index=True,
        description="The job type"
    )
    priority: JobPriority = Field(
        default=JobPriority.LOW,
        index=True,
        description="The job priority"
    )
    status: JobStatus = Field(
        index=True,
        default=JobStatus.PENDING,
        description="Current status"
    )
    progress: int = Field(
        default=0,
        description="Download progress percentage"
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

    @computed_field  # type: ignore[misc]
    @property
    def is_completed(self) -> bool:
        return self.status in [
            JobStatus.FAILED,
            JobStatus.SUCCESS,
            JobStatus.CANCELED,
        ]


@event.listens_for(Job, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: Job):
    if target.error and not target.is_completed:
        if target.error.startswith('Canceled'):
            target.status = JobStatus.CANCELED
        else:
            target.status = JobStatus.FAILED
    if not target.started_at and target.status != JobStatus.PENDING:
        target.started_at = current_timestamp()
    if not target.finished_at and target.is_completed:
        target.finished_at = current_timestamp()
