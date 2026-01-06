from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List

import models, schemas, auth
from database import SessionLocal, get_db, create_tables
from auth import verify_token, get_token


# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()

    db = SessionLocal()
    try:
        existing_teachers = db.query(models.Teacher).count()
        if existing_teachers == 0:
            print("No teachers found, creating sample data...")

            teachers_data = [
                {
                    "username": "karelina_math",
                    "full_name": "Карелина Наталья Александровна",
                    "subject": "Математика",
                    "password": "math123",
                },
                {
                    "username": "chestnih_lit",
                    "full_name": "Честных Евгения Ивановна",
                    "subject": "Литература",
                    "password": "lit123",
                },
                {
                    "username": "gordeev_phys",
                    "full_name": "Гордеев Дмитрий Александрович",
                    "subject": "Физика",
                    "password": "phys123",
                },
            ]

            for teacher_data in teachers_data:
                teacher = models.Teacher(
                    username=teacher_data["username"],
                    full_name=teacher_data["full_name"],
                    subject=teacher_data["subject"],
                    password_hash=auth.get_password_hash(teacher_data["password"]),
                )
                db.add(teacher)

            db.commit()
            print("Sample teachers created successfully")
        else:
            print(f"Database already contains {existing_teachers} teachers")

    except Exception as e:
        print(f"Error during initialization: {e}")
        db.rollback()
    finally:
        db.close()

    yield


app = FastAPI(title="School Praise API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get current teacher
async def get_current_teacher(
    token: str = Depends(get_token), db: Session = Depends(get_db)
):
    teacher_id = verify_token(token)
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


# Teacher endpoints
@app.get("/teachers", response_model=List[schemas.Teacher])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(models.Teacher).all()
    return teachers


@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


# Auth endpoints
@app.post("/auth/login", response_model=schemas.LoginResponse)
def teacher_login(credentials: schemas.LoginCredentials, db: Session = Depends(get_db)):
    teacher = (
        db.query(models.Teacher)
        .filter(models.Teacher.username == credentials.username)
        .first()
    )

    if not teacher or not auth.verify_password(
        credentials.password, teacher.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = auth.create_access_token(data={"sub": teacher.id})

    return {"teacher": teacher, "token": access_token}


@app.get("/auth/me", response_model=schemas.Teacher)
def get_current_user(current_teacher: models.Teacher = Depends(get_current_teacher)):
    return current_teacher


# Praise endpoints
@app.post("/praise", response_model=dict)
def send_praise(praise: schemas.PraiseMessageCreate, db: Session = Depends(get_db)):
    # Check if teacher exists
    teacher = (
        db.query(models.Teacher).filter(models.Teacher.id == praise.teacher_id).first()
    )
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # Create praise message
    db_praise = models.PraiseMessage(
        teacher_id=praise.teacher_id,
        message=praise.message,
        is_anonymous=praise.is_anonymous,
        user_name=praise.user_name if not praise.is_anonymous else None,
    )

    db.add(db_praise)
    db.commit()

    return {"success": True}


@app.get("/praise/teacher/{teacher_id}", response_model=List[schemas.PraiseMessage])
def get_teacher_praise(
    teacher_id: str,
    current_teacher: models.Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
):
    # Ensure teacher can only access their own praise messages
    if current_teacher.id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these messages",
        )

    praise_messages = (
        db.query(models.PraiseMessage)
        .filter(models.PraiseMessage.teacher_id == teacher_id)
        .order_by(models.PraiseMessage.created_at.desc())
        .all()
    )

    return praise_messages


@app.get("/")
def read_root():
    return {"message": "School Praise API is running!"}
