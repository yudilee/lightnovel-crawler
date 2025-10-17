from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from ...dao.user import User, UserRole, UserTier


class LoginRequest(BaseModel):
    email: str = Field(description="User email")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    token: str = Field(description="The authorization token")


class LoginResponse(TokenResponse):
    user: User = Field(description="The user")
    is_verified: bool = Field(description="Is the email verified")


class SignupRequest(BaseModel):
    email: EmailStr = Field(description="User Email")
    password: str = Field(description="User password")
    name: Optional[str] = Field(default=None, description="Full name")


class CreateRequest(SignupRequest):
    role: UserRole = Field(default=UserRole.USER, description="User role")
    tier: UserTier = Field(default=UserTier.BASIC, description="User tier")


class UpdateRequest(BaseModel):
    password: Optional[str] = Field(default=None, description="User password")
    name: Optional[str] = Field(default=None, description="Full name")
    role: Optional[UserRole] = Field(default=None, description="User role")
    is_active: Optional[bool] = Field(default=None, description="Active status")
    tier: Optional[UserTier] = Field(default=None, description="User tier")


class PasswordUpdateRequest(BaseModel):
    new_password: str = Field(description="New password")
    old_password: str = Field(description="Current password")


class NameUpdateRequest(BaseModel):
    name: str = Field(description="Full name")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(description="User Email")


class ResetPasswordRequest(BaseModel):
    password: Optional[str] = Field(default=None, description="User password")
