from sqlalchemy import Column, Integer, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String[50], unique=True)
    password = Column(String[50])
    username = Column(String[50])

    # items = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True)
    title = Column(String[50])
    completed = Column(Boolean)
    # user_id = Column(Integer, ForeignKey("users.id"))
    
    # owner = relationship("User", back_populates="tasks")

class SessionData(Base):
    __tablename__ = "sessions"

    session_id = Column(UUID, unique=True, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))

