from pydantic import BaseModel, Field


class JobProgress(BaseModel):
    job_id: str = Field(description='Job ID')
    done: int = Field(description='Completed child job')
    total: int = Field(description='Total child job count')
    percent: int = Field(description='Progress percentage (between 0 to 100)')
