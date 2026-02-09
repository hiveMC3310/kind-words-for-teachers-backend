from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from auth import get_token, verify_token
from config import ROLE_ADMIN, logger
from database import get_db


# Dependency to get current teacher
async def get_current_teacher(
    token: str = Depends(get_token), db: AsyncSession = Depends(get_db)
):
    """Получение текущего аутентифицированного преподавателя"""
    try:
        teacher_id = verify_token(token)

        result = await db.execute(
            select(models.Teacher).where(models.Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Преподаватель не найден"
            )

        return teacher

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при получении преподавателя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных преподавателя",
        )


# Dependency to get admin
async def get_current_admin(
    current_teacher: models.Teacher = Depends(get_current_teacher),
):
    """Получение текущего администратора"""
    if current_teacher.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_teacher
