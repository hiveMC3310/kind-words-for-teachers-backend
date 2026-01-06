from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid


def generate_uuid():
    return str(uuid.uuid4())


Base = declarative_base()


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)

    praise_messages = relationship("PraiseMessage", back_populates="teacher")


class PraiseMessage(Base):
    __tablename__ = "praise_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    teacher_id = Column(
        String(36), ForeignKey("teachers.id"), nullable=False, index=True
    )
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_anonymous = Column(Boolean, default=True)
    user_name = Column(String(100), nullable=True)

    teacher = relationship("Teacher", back_populates="praise_messages")
