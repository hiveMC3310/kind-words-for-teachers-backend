from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Teacher schemas
class TeacherBase(BaseModel):
    username: str
    full_name: str
    subject: str


class TeacherCreate(TeacherBase):
    password: str


class Teacher(TeacherBase):
    id: str

    class Config:
        from_attributes = True


# Praise schemas
class PraiseMessageBase(BaseModel):
    message: str
    is_anonymous: bool = True
    user_name: Optional[str] = None


class PraiseMessageCreate(PraiseMessageBase):
    teacher_id: str


class PraiseMessage(PraiseMessageBase):
    id: str
    teacher_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class LoginCredentials(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    teacher: Teacher
    token: str


class TokenData(BaseModel):
    teacher_id: Optional[str] = None
