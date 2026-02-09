from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import auth
import models
import schemas
from config import logger
from database import get_db
from utils import get_current_teacher

router = APIRouter()


# Auth endpoints
@router.post("/auth/login", response_model=schemas.LoginResponse)
async def teacher_login(
    credentials: schemas.LoginCredentials, db: AsyncSession = Depends(get_db)
):
    """Аутентификация преподавателя"""
    try:

        result = await db.execute(
            select(models.Teacher).where(
                models.Teacher.username == credentials.username
            )
        )
        teacher = result.scalar_one_or_none()

        if not teacher or not auth.verify_password(
            credentials.password, teacher.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = auth.create_access_token(data={"sub": teacher.id})

        return {"teacher": teacher, "token": access_token}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при аутентификации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при аутентификации",
        )


@router.get("/auth/me", response_model=schemas.Teacher)
async def get_current_user(
    current_teacher: models.Teacher = Depends(get_current_teacher),
):
    """Получение информации о текущем пользователе"""
    return current_teacher
