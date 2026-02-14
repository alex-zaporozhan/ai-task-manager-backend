from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from src.domain.entities import UserRole, TaskStatus, TaskPriority, Currency


# --- TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str


# --- DEPARTMENT ---
class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2)


class DepartmentRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- USER ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    department_id: Optional[UUID] = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole
    department_id: Optional[UUID]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserAdminUpdate(BaseModel):
    """
    Схема для полного управления пользователем со стороны Админа.
    Все поля опциональны: меняем только то, что передали.
    """
    role: Optional[UserRole] = None
    department_id: Optional[UUID] = None
    full_name: Optional[str] = None


# --- COMMENT ---
class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1)


class CommentRead(BaseModel):
    id: UUID
    author_id: UUID
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- TASK ---
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    target_dept_id: Optional[UUID] = None
    deadline: Optional[datetime] = None
    budget: Decimal = Field(default=Decimal("0.0"))
    currency: Currency = Currency.USD
    executor_id: Optional[UUID] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskAssign(BaseModel):
    executor_id: UUID


class TaskRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    owner_id: UUID
    executor_id: Optional[UUID]
    target_dept_id: Optional[UUID]
    status: TaskStatus
    priority: TaskPriority
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    budget: Decimal
    currency: Currency

    class Config:
        from_attributes = True


class OrderPublicRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True