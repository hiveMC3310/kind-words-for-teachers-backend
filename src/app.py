import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import auth
import models
from config import ROLE_ADMIN, ROLE_TEACHER, logger, settings
from database import create_tables, get_db_context
from handlers import main_router


async def init_database():
    """Инициализация базы данных"""
    try:
        await create_tables()

        async with get_db_context() as db:
            # Проверяем существующих преподавателей

            result = await db.execute(select(models.Teacher))
            existing_teachers = len(result.scalars().all())

            if existing_teachers == 0:
                logger.info("Нет преподавателей, создаем тестовые данные...")

                for teacher_data in settings.TEACHERS_DATA:
                    teacher = models.Teacher(
                        username=teacher_data["username"],
                        full_name=teacher_data["full_name"],
                        subject=teacher_data["subject"],
                        password_hash=auth.get_password_hash(teacher_data["password"]),
                        role=ROLE_TEACHER,
                    )
                    db.add(teacher)

                await db.commit()
                logger.info("Тестовые преподаватели созданы успешно")
            else:
                logger.info(
                    f"В базе данных уже есть {existing_teachers} преподавателей"
                )

            # Проверяем и создаем администратора
            admin_result = await db.execute(
                select(models.Teacher).where(
                    models.Teacher.username == settings.ADMIN_USERNAME
                )
            )
            admin = admin_result.scalar_one_or_none()

            if not admin:
                logger.info("Создаем учетную запись администратора...")
                admin = models.Teacher(
                    username=settings.ADMIN_USERNAME,
                    full_name=settings.ADMIN_FULL_NAME,
                    subject="Директор",
                    password_hash=auth.get_password_hash(settings.ADMIN_PASSWORD),
                    role=ROLE_ADMIN,
                )
                db.add(admin)
                await db.commit()
                logger.info(f"Администратор {admin.full_name} создан успешно")
            else:
                logger.info("Администратор уже существует")

    except IntegrityError as e:
        logger.error(f"Ошибка целостности данных: {e}")
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных: {e}")
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        logger.error(traceback.format_exc())


# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Запуск приложения...")
    # Инициализация базы данных
    await init_database()

    yield

    logger.info("Остановка приложения...")


app = FastAPI(
    title="School Praise API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(main_router)


# Глобальный обработчик исключений
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Глобальная ошибка: {exc}")
    logger.error(traceback.format_exc())

    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера"},
    )


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "service": "school-praise-api", "version": "1.0.0"}


@app.get("/")
async def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "School Praise API работает!",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health",
    }
