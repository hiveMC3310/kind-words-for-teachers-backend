import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class Role:
    TEACHER = "teacher"
    ADMIN = "admin"


# Teacher schemas
class TeacherBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Имя пользователя (только буквы, цифры и _)",
    )
    full_name: str = Field(
        ..., min_length=5, max_length=100, description="Полное имя преподавателя"
    )
    subject: str = Field(
        ..., min_length=2, max_length=100, description="Предмет преподавания"
    )
    role: str = Field(default=Role.TEACHER, description="Роль пользователя")


class TeacherCreate(TeacherBase):
    password: str = Field(
        ..., min_length=6, max_length=100, description="Пароль минимум 6 символов"
    )


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = Field(
        None, min_length=5, max_length=100, description="Полное имя преподавателя"
    )
    subject: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Предмет преподавания"
    )
    password: Optional[str] = Field(
        None, min_length=6, max_length=100, description="Новый пароль"
    )


class Teacher(TeacherBase):
    id: str

    class Config:
        from_attributes = True


# Praise schemas
class PraiseMessageBase(BaseModel):
    message: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Текст сообщения (5-1000 символов)",
    )
    is_anonymous: bool = Field(default=True, description="Анонимное сообщение")
    user_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Имя отправителя"
    )

    @validator("message")
    def validate_message(cls, v):
        # Проверка на недопустимые символы
        if re.search(r"[<>{}[\]]", v):
            raise ValueError("Сообщение содержит недопустимые символы")
        return v.strip()

    @validator("user_name")
    def validate_user_name(cls, v, values):
        if not values.get("is_anonymous") and not v:
            raise ValueError("Имя отправителя обязательно для неанонимных сообщений")
        return v


class PraiseMessageCreate(PraiseMessageBase):
    teacher_id: str = Field(
        ...,
        description="ID преподавателя",
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
    )


class PraiseMessage(PraiseMessageBase):
    id: str
    teacher_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Admin schemas
class AdminStats(BaseModel):
    total_teachers: int
    total_praises: int
    praises_last_week: int


# Auth schemas
class LoginCredentials(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginResponse(BaseModel):
    teacher: Teacher
    token: str


class TokenData(BaseModel):
    teacher_id: Optional[str] = None
