from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from config import logger
from database import get_db
from utils import get_current_teacher

router = APIRouter()


# Praise endpoints
@router.post("/praise", response_model=dict)
async def send_praise(
    praise: schemas.PraiseMessageCreate, db: AsyncSession = Depends(get_db)
):
    """Отправка благодарности преподавателю"""
    try:
        # Проверка существования преподавателя

        result = await db.execute(
            select(models.Teacher).where(models.Teacher.id == praise.teacher_id)
        )
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Преподаватель не найден"
            )

        # Создание сообщения благодарности
        db_praise = models.PraiseMessage(
            teacher_id=praise.teacher_id,
            message=praise.message,
            is_anonymous=praise.is_anonymous,
            user_name=praise.user_name if not praise.is_anonymous else None,
        )

        db.add(db_praise)
        await db.commit()
        await db.refresh(db_praise)

        return {
            "success": True,
            "message": "Благодарность отправлена успешно",
            "praise_id": db_praise.id,
        }

    except HTTPException:
        await db.rollback()
        raise
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Ошибка целостности данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при сохранении данных",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка базы данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении данных",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@router.get("/praise/teacher/{teacher_id}", response_model=List[schemas.PraiseMessage])
async def get_teacher_praise(
    teacher_id: str,
    current_teacher: models.Teacher = Depends(get_current_teacher),
    db: AsyncSession = Depends(get_db),
):
    """Получение сообщений для конкретного преподавателя"""
    try:
        # Проверка авторизации
        if current_teacher.id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к данным другого преподавателя",
            )

        result = await db.execute(
            select(models.PraiseMessage)
            .where(models.PraiseMessage.teacher_id == teacher_id)
            .order_by(models.PraiseMessage.created_at.desc())
        )
        praise_messages = result.scalars().all()

        return praise_messages

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении благодарностей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных",
        )
