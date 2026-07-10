from typing import Literal
from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    userId: int
    username: str
    email: str
    phone: str = ""
    role: Literal["buyer", "seller"]
    shopName: str | None = None
    mainCategory: str | None = None
    status: str = "active"
    createdAt: str
    updatedAt: str


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    email: str
    password: str = Field(min_length=6)
    phone: str | None = ""
    role: Literal["buyer", "seller"] = "buyer"
    shopName: str | None = None
    mainCategory: str | None = None


class UpdateProfileRequest(BaseModel):
    username: str | None = None
    phone: str | None = None
