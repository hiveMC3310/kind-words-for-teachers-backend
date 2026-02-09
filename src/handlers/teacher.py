from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from config import logger
from database import get_db

router = APIRouter()
# Teacher endpoints


@router.get("/teachers", response_model=List[schemas.Teacher])
async def get_teachers(db: AsyncSession = Depends(get_db)):
    """Получение списка всех преподавателей"""
    try:

        result = await db.execute(select(models.Teacher))
        teachers = result.scalars().all()
        return teachers
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении преподавателей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных преподавателей",
        )


@router.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
async def get_teacher(teacher_id: str, db: AsyncSession = Depends(get_db)):
    """Получение информации о конкретном преподавателе"""
    try:

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
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении преподавателя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных преподавателя",
        )
