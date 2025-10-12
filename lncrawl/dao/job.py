from typing import Any, Dict, Optional

from sqlalchemy import event
from sqlmodel import JSON, BigInteger, Column, Field

from ..utils.time_utils import current_timestamp
from ._base import BaseTable
from .enums import JobPriority, JobStatus, RunState


class Job(BaseTable, table=True):
    url: str = Field(
        description="Download link"
    )

    user_id: str = Field(
        foreign_key="user.id",
        ondelete='CASCADE'
    )
    novel_id: Optional[str] = Field(
        foreign_key="novel.id",
        ondelete='SET NULL'
    )

    priority: JobPriority = Field(
        default=JobPriority.LOW,
        index=True,
        description="The job priority"
    )
    status: JobStatus = Field(
        default=JobStatus.PENDING,
        index=True,
        description="Current status"
    )
    run_state: Optional[RunState] = Field(
        default=None,
        description="State of the job in progress status"
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

    extra: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON),
        description="Extra field"
    )


@event.listens_for(Job, "before_update", propagate=True)
def auto_update_timestamp(mapper, connection, target: Job):
    if target.error and target.run_state not in [
        RunState.FAILED,
        RunState.SUCCESS,
        RunState.CANCELED,
    ]:
        if target.error.startswith('Canceled'):
            target.run_state = RunState.CANCELED
        else:
            target.run_state = RunState.FAILED
    if not target.started_at and target.status != JobStatus.PENDING:
        target.started_at = current_timestamp()
    if not target.finished_at and target.status == JobStatus.COMPLETED:
        target.finished_at = current_timestamp()
