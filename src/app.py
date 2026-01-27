import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import auth
import models
import schemas
from auth import get_token, verify_token
from config import settings
from database import create_tables, get_db, get_db_context

# Константы для ролей
ROLE_TEACHER = "teacher"
ROLE_ADMIN = "admin"


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

                teachers_data = [
                    {
                        "username": "Antipova",
                        "full_name": "Антипова Елена Анатольевна",
                        "subject": "Учитель математики",
                        "password": "Ant_rvpG8O",
                    },
                    {
                        "username": "Astarkina",
                        "full_name": "Астаркина Марина Вячеславовна",
                        "subject": "Социальный педагог/учитель истории и права",
                        "password": "Ast_b$Kv*Y",
                    },
                    {
                        "username": "Belyaeva",
                        "full_name": "Беляева Ольга Михайловна",
                        "subject": "Учитель физической культуры",
                        "password": "Bel_&8pcn0",
                    },
                    {
                        "username": "Bobileva",
                        "full_name": "Бобылева Светлана Валерьевна",
                        "subject": "Учитель начальных классов",
                        "password": "Bob_9E@WR8",
                    },
                    {
                        "username": "Bordacheva",
                        "full_name": "Бордачева Ирина Николаевна",
                        "subject": "Учитель начальных классов",
                        "password": "Bor_ELzALT",
                    },
                    {
                        "username": "Vilgelm",
                        "full_name": "Вильгельм Елена Геннадьевна",
                        "subject": "Учитель химии",
                        "password": "Vil_2G8Sr4",
                    },
                    {
                        "username": "Vinyukova",
                        "full_name": "Винюкова Анна Николаевна",
                        "subject": "Учитель начальных классов",
                        "password": "Vin_%0Zejm",
                    },
                    {
                        "username": "Goncharova",
                        "full_name": "Гончарова Ирина Владимировна",
                        "subject": "Учитель начальных классов",
                        "password": "Gon_AV2?ei",
                    },
                    {
                        "username": "Gordeev",
                        "full_name": "Гордеев Дмитрий Александрович",
                        "subject": "Учитель физики",
                        "password": "Gor_zM40de",
                    },
                    {
                        "username": "Grishenko",
                        "full_name": "Гришенко Галина Вячеславовна",
                        "subject": "Учитель начальных классов",
                        "password": "Gri_ZxsQoN",
                    },
                    {
                        "username": "Egorushkina",
                        "full_name": "Егорушкина Татьяна Григорьевна",
                        "subject": "Учитель начальных классов",
                        "password": "Ego_n7EAFx",
                    },
                    {
                        "username": "Zhelacskaya",
                        "full_name": "Желавская Светлана  Александровна",
                        "subject": "Учитель начальных классов",
                        "password": "Zhe_#yDGgi",
                    },
                    {
                        "username": "Zhigunkova",
                        "full_name": "Жигункова Нина Геннадьевна",
                        "subject": "Учитель английского языка",
                        "password": "Zhi_HJBkqR",
                    },
                    {
                        "username": "Ivanova",
                        "full_name": "Иванова Галина Анатольевна",
                        "subject": "Учитель истории, обществознания",
                        "password": "Iva_Hsrt^M",
                    },
                    {
                        "username": "Karelina",
                        "full_name": "Карелина Наталья Александровна",
                        "subject": "Учитель математики, информатики",
                        "password": "Kar_TuP5ul",
                    },
                    {
                        "username": "Koldashova",
                        "full_name": "Колдашова Елена Николаевна",
                        "subject": "Учитель русского языка и литературы",
                        "password": "Kol_258T0E",
                    },
                    {
                        "username": "Kolina",
                        "full_name": "Колина Тамара Николаевна",
                        "subject": "Учитель начальных классов",
                        "password": "Kol_PTC@yt",
                    },
                    {
                        "username": "Kondrushina",
                        "full_name": "Кондрушина Алла Викторовна",
                        "subject": "Учитель начальных классов",
                        "password": "Kon_lqt!wS",
                    },
                    {
                        "username": "Korshunova",
                        "full_name": "Коршунова Ольга Викторовна",
                        "subject": "Учитель английского языка",
                        "password": "Kor_wr@4U2",
                    },
                    {
                        "username": "Kostina",
                        "full_name": "Костина Наталья Александровна",
                        "subject": "Учитель математики",
                        "password": "Kos_oIPsT4",
                    },
                    {
                        "username": "Kryuchokva",
                        "full_name": "Крючкова Елена Викторовна",
                        "subject": "Учитель начальных классов",
                        "password": "Kry_G*$J5@",
                    },
                    {
                        "username": "Kuznetsova",
                        "full_name": "Кузнецова Марина Викторовна",
                        "subject": "Учитель начальных классов",
                        "password": "Kuz_*yqgL2",
                    },
                    {
                        "username": "Kotkova",
                        "full_name": "Коткова Виктория Викторовна",
                        "subject": "Учитель русского языка и литературы",
                        "password": "Kot_FdT8^L",
                    },
                    {
                        "username": "Kuptsova",
                        "full_name": "Купцова Ольга Николаевна",
                        "subject": "Учитель начальных классов",
                        "password": "Kup_%41^DD",
                    },
                    {
                        "username": "Kagutina",
                        "full_name": "Лагутина Наталия Михайловна",
                        "subject": "Учитель английского языка",
                        "password": "Kag_yqk8z%",
                    },
                    {
                        "username": "Liseva",
                        "full_name": "Лисева Галина Викторовна",
                        "subject": "Учитель начальных классов",
                        "password": "Lis_7eYeDD",
                    },
                    {
                        "username": "Matyushkina",
                        "full_name": "Матюшкина Ольга Вячеславовна",
                        "subject": "Учитель, руководитель хорового коллектива",
                        "password": "Mat_%TkYfJ",
                    },
                    {
                        "username": "Mihailova",
                        "full_name": "Михайлова Юлия Игоревна",
                        "subject": "Воспитатель",
                        "password": "Mih_Z32!G@",
                    },
                    {
                        "username": "Misina",
                        "full_name": "Мысина Олеся Васильевна",
                        "subject": "Учитель истории, обществознания",
                        "password": "Mis_deJjvN",
                    },
                    {
                        "username": "Nazarova",
                        "full_name": "Назарова Оксана Александровна",
                        "subject": "Учитель информатики",
                        "password": "Naz_C@46pR",
                    },
                    {
                        "username": "Seliverstova",
                        "full_name": "Селиверстова Светлана Михайловна",
                        "subject": "Учитель физической культуры",
                        "password": "Sel_hRKzMC",
                    },
                    {
                        "username": "Soroka",
                        "full_name": "Сорока Юрий Григорьевич",
                        "subject": "Преподаватель-организатор ОБЗР",
                        "password": "Sor_tXsMq@",
                    },
                    {
                        "username": "Stenina",
                        "full_name": "Стенина Любовь Владимировна",
                        "subject": "Учитель начальных классов",
                        "password": "Ste_NG46Vo",
                    },
                    {
                        "username": "Strochkova",
                        "full_name": "Строчкова Людмила Викторовна",
                        "subject": "Учитель математики, физики",
                        "password": "Str_99Th9c",
                    },
                    {
                        "username": "Suslova",
                        "full_name": "Суслова Оксана Вячеславовна",
                        "subject": "Учитель русского языка и литературы",
                        "password": "Sus_4QX&X@",
                    },
                    {
                        "username": "Komarov",
                        "full_name": "Комарова Оксана Сергеевна",
                        "subject": "Учитель технологии",
                        "password": "Kom_QbMH6b",
                    },
                    {
                        "username": "Titova",
                        "full_name": "Титова Ольга Сергеевна",
                        "subject": "Педагог дополнительного образования",
                        "password": "Tit_JkAULh",
                    },
                    {
                        "username": "Fadeeva",
                        "full_name": "Фадеева Александра Вячеславовна",
                        "subject": "Учитель английского языка",
                        "password": "Fad_#0Wz3s",
                    },
                    {
                        "username": "Fetisova",
                        "full_name": "Фетисова Елена Ивановна",
                        "subject": "Учитель биологии",
                        "password": "Fet_#NcxEx",
                    },
                    {
                        "username": "Filatov",
                        "full_name": "Филатов  Александр Владимирович",
                        "subject": "Учитель технологии",
                        "password": "Fil_zI#wjP",
                    },
                    {
                        "username": "Chernechkova",
                        "full_name": "Чернечкова Наталья Валерьевна",
                        "subject": "Учитель математики",
                        "password": "Che_Hk*VIK",
                    },
                    {
                        "username": "Chestnih",
                        "full_name": "Честных Евгения Ивановна",
                        "subject": "Учитель русского языка и литературы",
                        "password": "Che_Gc!2j*",
                    },
                    {
                        "username": "Yarotskaya",
                        "full_name": "Яроцкая Татьяна Викторовна",
                        "subject": "Учитель математики",
                        "password": "Yar_Uq1%nr",
                    },
                    {
                        "username": "Vyushina",
                        "full_name": "Вьюшина Наталья Александровна",
                        "subject": "Учитель иностранного языка",
                        "password": "Vyu_kNshRp",
                    },
                    {
                        "username": "Buyankina",
                        "full_name": "Буянкина Надежда Валерьевна",
                        "subject": "Советник по воспитанию",
                        "password": "Buy_wT8@Mw",
                    },
                    {
                        "username": "Kotina",
                        "full_name": "Котина Марина Владимировна",
                        "subject": "Учитель ИЗО",
                        "password": "Kot_rYB07K",
                    },
                    {
                        "username": "Zhuravleva",
                        "full_name": "Журавлева Виктория Вячеславовна",
                        "subject": "Учитель русского языка и литературы",
                        "password": "Zhu_32KbUY",
                    },
                ]

                for teacher_data in teachers_data:
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
                logger.info("Администратор создан успешно")
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


# Health check
@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {"status": "healthy", "service": "school-praise-api", "version": "1.0.0"}


# Teacher endpoints
@app.get("/teachers", response_model=List[schemas.Teacher])
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


@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
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


# Auth endpoints
@app.post("/auth/login", response_model=schemas.LoginResponse)
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


@app.get("/auth/me", response_model=schemas.Teacher)
async def get_current_user(
    current_teacher: models.Teacher = Depends(get_current_teacher),
):
    """Получение информации о текущем пользователе"""
    return current_teacher


# Praise endpoints
@app.post("/praise", response_model=dict)
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


@app.get("/praise/teacher/{teacher_id}", response_model=List[schemas.PraiseMessage])
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


# Admin endpoints
@app.get("/admin/stats", response_model=schemas.AdminStats)
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


@app.post("/admin/teachers", response_model=schemas.Teacher)
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


@app.put("/admin/teachers/{teacher_id}", response_model=schemas.Teacher)
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


@app.delete("/admin/teachers/{teacher_id}")
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


@app.get("/admin/praises", response_model=List[schemas.PraiseMessage])
async def get_all_praises(
    current_admin: models.Teacher = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
):
    """Получение всех благодарностей (только для администратора)"""
    try:
        result = await db.execute(
            select(models.PraiseMessage)
            .order_by(models.PraiseMessage.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        praises = result.scalars().all()

        return praises

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении благодарностей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных",
        )


@app.get("/")
async def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "School Praise API работает!",
        "version": "1.0.0",
        "docs": "/docs",
        "health_check": "/health",
    }
