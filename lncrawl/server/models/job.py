from typing import List, Optional

from pydantic import BaseModel, Field

from ...dao import Artifact, Job, Novel, User
from ...dao.enums import JobStatus, RunState


class JobDetail(BaseModel):
    job: Job = Field(description='Job')
    user: Optional[User] = Field(description='User')
    novel: Optional[Novel] = Field(description='Novel')
    artifacts: Optional[List[Artifact]] = Field(description='Artifacts')


class JobRunnerHistoryItem(BaseModel):
    time: int = Field(description='UNIX timestamp (seconds)')
    job_id: str = Field(description='Job')
    user_id: str = Field(description='User')
    novel_id: Optional[str] = Field(description='Novel')
    status: JobStatus = Field(description="Current status")
    run_state: Optional[RunState] = Field(description="State of the job in progress status")


class JobRunnerHistory(BaseModel):
    running: bool = Field(description='Job runner status')
    history: List[JobRunnerHistoryItem] = Field(description='Runner history')
