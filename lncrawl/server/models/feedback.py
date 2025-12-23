from typing import Optional

from pydantic import BaseModel, Field

from ...dao import FeedbackStatus, FeedbackType


class FeedbackCreateRequest(BaseModel):
    type: FeedbackType = Field(description="Type of feedback")
    subject: str = Field(description="Subject/title of the feedback", min_length=1, max_length=200)
    message: str = Field(description="Detailed message/description", min_length=1, max_length=5000)


class FeedbackUpdateRequest(BaseModel):
    type: Optional[FeedbackType] = Field(default=None, description="Type of feedback")
    subject: Optional[str] = Field(default=None, description="Subject/title of the feedback", min_length=1, max_length=200)
    message: Optional[str] = Field(default=None, description="Detailed message/description", min_length=1, max_length=5000)


class FeedbackRespondRequest(BaseModel):
    status: FeedbackStatus = Field(description="Status of the feedback")
    admin_notes: str = Field(description="Admin notes/response", min_length=1, max_length=5000)
