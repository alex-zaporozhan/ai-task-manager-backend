from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from src.domain.entities import UserRole, TaskStatus, TaskPriority

class Base(DeclarativeBase):
    pass

class DepartmentModel(Base):
    __tablename__ = "departments"
    id: Mapped[UUID] = orm.mapped_column(sa.UUID, primary_key=True, default=uuid4)
    name: Mapped[str] = orm.mapped_column(sa.String(100), unique=True, nullable=False)
    # ИСПРАВЛЕНО: Добавлен timezone=True
    created_at: Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', now())"))
    users = relationship("UserModel", back_populates="department")
    tasks = relationship("TaskModel", back_populates="target_dept")

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = orm.mapped_column(sa.UUID, primary_key=True, default=uuid4)
    email: Mapped[str] = orm.mapped_column(sa.String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    full_name: Mapped[str] = orm.mapped_column(sa.String(100), nullable=False)
    role: Mapped[str] = orm.mapped_column(sa.String(20), default=UserRole.EMPLOYEE.value)
    is_active: Mapped[bool] = orm.mapped_column(sa.Boolean, default=True)
    department_id: Mapped[Optional[UUID]] = orm.mapped_column(sa.ForeignKey("departments.id"), nullable=True)
    # ИСПРАВЛЕНО: Добавлен timezone=True
    created_at: Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', now())"))
    department = relationship("DepartmentModel", back_populates="users")
    owned_tasks = relationship("TaskModel", back_populates="owner", foreign_keys="TaskModel.owner_id")
    executed_tasks = relationship("TaskModel", back_populates="executor", foreign_keys="TaskModel.executor_id")
    comments = relationship("CommentModel", back_populates="author")

class TaskModel(Base):
    __tablename__ = "tasks"
    id: Mapped[UUID] = orm.mapped_column(sa.UUID, primary_key=True, default=uuid4)
    title: Mapped[str] = orm.mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = orm.mapped_column(sa.String, nullable=True)
    owner_id: Mapped[UUID] = orm.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    executor_id: Mapped[Optional[UUID]] = orm.mapped_column(sa.ForeignKey("users.id"), nullable=True)
    target_dept_id: Mapped[Optional[UUID]] = orm.mapped_column(sa.ForeignKey("departments.id"), nullable=True)
    status: Mapped[str] = orm.mapped_column(sa.String(20), default=TaskStatus.NEW.value)
    priority: Mapped[str] = orm.mapped_column(sa.String(20), default=TaskPriority.MEDIUM.value)
    # ИСПРАВЛЕНО: Добавлен timezone=True
    deadline: Mapped[Optional[datetime]] = orm.mapped_column(sa.DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', now())"), onupdate=datetime.now)

    owner = relationship("UserModel", foreign_keys=[owner_id], back_populates="owned_tasks")
    executor = relationship("UserModel", foreign_keys=[executor_id], back_populates="executed_tasks")
    target_dept = relationship("DepartmentModel", back_populates="tasks")
    comments = relationship("CommentModel", back_populates="task", cascade="all, delete-orphan")

class CommentModel(Base):
    __tablename__ = "comments"
    id: Mapped[UUID] = orm.mapped_column(sa.UUID, primary_key=True, default=uuid4)
    text: Mapped[str] = orm.mapped_column(sa.String, nullable=False)
    task_id: Mapped[UUID] = orm.mapped_column(sa.ForeignKey("tasks.id"), nullable=False)
    author_id: Mapped[UUID] = orm.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    # ИСПРАВЛЕНО: Добавлен timezone=True
    created_at: Mapped[datetime] = orm.mapped_column(sa.DateTime(timezone=True), server_default=sa.text("TIMEZONE('utc', now())"))
    task = relationship("TaskModel", back_populates="comments")
    author = relationship("UserModel", back_populates="comments")