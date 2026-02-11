from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import auth
import models
import schemas
from config import logger
from database import get_db
from utils import get_current_admin

router = APIRouter()


# Admin endpoints
@router.get("/admin/stats", response_model=schemas.AdminStats)
async def get_admin_stats(
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Получение статистики для администратора"""
    try:
        # Общее количество учителей
        total_teachers_result = await db.execute(
            select(func.count()).select_from(models.Teacher)
        )
        total_teachers = total_teachers_result.scalar()

        # Общее количество благодарностей
        total_praises_result = await db.execute(
            select(func.count()).select_from(models.PraiseMessage)
        )
        total_praises = total_praises_result.scalar()

        # Благодарности за последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)
        praises_last_week_result = await db.execute(
            select(func.count()).where(models.PraiseMessage.created_at >= week_ago)
        )
        praises_last_week = praises_last_week_result.scalar()

        return schemas.AdminStats(
            total_teachers=total_teachers,
            total_praises=total_praises,
            praises_last_week=praises_last_week,
        )

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении статистики",
        )


@router.post("/admin/teachers", response_model=schemas.Teacher)
async def create_teacher(
    teacher_data: schemas.TeacherCreate,
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Создание нового преподавателя (только для администратора)"""
    try:
        # Проверяем, существует ли уже пользователь с таким username
        existing_result = await db.execute(
            select(models.Teacher).where(
                models.Teacher.username == teacher_data.username
            )
        )
        existing_teacher = existing_result.scalar_one_or_none()

        if existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует",
            )

        # Создаем нового преподавателя
        new_teacher = models.Teacher(
            username=teacher_data.username,
            full_name=teacher_data.full_name,
            subject=teacher_data.subject,
            password_hash=auth.get_password_hash(teacher_data.password),
            role=teacher_data.role,
        )

        db.add(new_teacher)
        await db.commit()
        await db.refresh(new_teacher)

        return new_teacher

    except HTTPException:
        await db.rollback()
        raise
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Ошибка целостности данных: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании пользователя",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании преподавателя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании преподавателя",
        )


@router.put("/admin/teachers/{teacher_id}", response_model=schemas.Teacher)
async def update_teacher(
    teacher_id: str,
    teacher_update: schemas.TeacherUpdate,
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Обновление информации о преподавателе (только для администратора)"""
    try:
        # Находим преподавателя
        result = await db.execute(
            select(models.Teacher).where(models.Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден",
            )

        # Обновляем поля
        if teacher_update.full_name is not None:
            teacher.full_name = teacher_update.full_name
        if teacher_update.subject is not None:
            teacher.subject = teacher_update.subject
        if teacher_update.password is not None:
            teacher.password_hash = auth.get_password_hash(teacher_update.password)

        await db.commit()
        await db.refresh(teacher)

        return teacher

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при обновлении преподавателя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении преподавателя",
        )


@router.delete("/admin/teachers/{teacher_id}")
async def delete_teacher(
    teacher_id: str,
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удаление преподавателя (только для администратора)"""
    try:
        # Нельзя удалить самого себя
        if current_admin.id == teacher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить собственную учетную запись",
            )

        # Находим преподавателя
        result = await db.execute(
            select(models.Teacher).where(models.Teacher.id == teacher_id)
        )
        teacher = result.scalar_one_or_none()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Преподаватель не найден",
            )

        await db.delete(teacher)
        await db.commit()

        return {"success": True, "message": "Преподаватель деактивирован"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при удалении преподавателя: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении преподавателя",
        )


@router.get("/admin/praises", response_model=List[schemas.PraiseMessageDetail])
async def get_all_praises(
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    """Получение всех благодарностей (только для администратора)"""
    try:
        result = await db.execute(
            select(
                models.PraiseMessage, models.Teacher.full_name, models.Teacher.subject
            )
            .join(models.Teacher, models.PraiseMessage.teacher_id == models.Teacher.id)
            .order_by(models.PraiseMessage.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = result.all()

        praises = []
        for row in rows:
            praise_dict = {
                **row.PraiseMessage.__dict__,
                "teacher_full_name": row.full_name,
                "teacher_subject": row.subject,
            }
            praises.append(schemas.PraiseMessageDetail(**praise_dict))

        return praises

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении благодарностей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных",
        )


@router.delete("/admin/praises/{praise_id}")
async def delete_praise_message(
    praise_id: str,
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Удаление благодарности (только для администратора)"""
    try:
        # Находим сообщение
        result = await db.execute(
            select(models.PraiseMessage).where(models.PraiseMessage.id == praise_id)
        )
        praise_message = result.scalar_one_or_none()

        if not praise_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сообщение не найдено",
            )

        # Удаляем сообщение
        await db.delete(praise_message)
        await db.commit()

        return {"success": True, "message": "Сообщение удалено"}

    except HTTPException:
        await db.rollback()
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка при удалении сообщения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении сообщения",
        )
