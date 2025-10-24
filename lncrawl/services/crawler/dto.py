from pydantic import BaseModel, Field


class LoginData(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password or token")
