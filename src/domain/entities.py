from datetime import datetime, timezone
from decimal import Decimal  # ВОТ ЭТОТ ИМПОРТ БЫЛ ПРОПУЩЕН
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, field_validator


# --- ENUMS (Константы) ---
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class TaskStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_REVIEW = "on_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


# --- DOMAIN ENTITIES ---

class Department(BaseModel):
    """Отдел компании."""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=2)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class User(BaseModel):
    """Сотрудник компании."""
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True
    department_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class Comment(BaseModel):
    """Комментарий к задаче."""
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    author_id: UUID
    text: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class Task(BaseModel):
    """Бизнес-задача."""
    id: UUID = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None

    owner_id: UUID
    executor_id: Optional[UUID] = None
    target_dept_id: Optional[UUID] = None

    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.MEDIUM

    # Бюджет и валюта для полноты картины
    budget: Decimal = Field(default=Decimal("0.0"))
    currency: Currency = Currency.USD

    deadline: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # --- ВАЛИДАТОРЫ ---
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Title must be at least 3 chars.")
        return v.strip()

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Исправляет ошибку сравнения offset-naive и offset-aware datetimes."""
        if v:
            # Если время пришло без часового пояса (naive), принудительно ставим ему UTC
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)

            # Теперь сравнение с текущим временем (тоже в UTC) будет корректным
            if v < datetime.now(timezone.utc):
                raise ValueError("Deadline cannot be in the past.")
        return v

    def update_status(self, new_status: TaskStatus) -> None:
        if self.status in (TaskStatus.DONE, TaskStatus.CANCELLED):
            raise ValueError(f"Cannot change status of a finished task.")
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def assign_executor(self, user_id: UUID) -> None:
        if user_id == self.owner_id:
            raise ValueError("Owner cannot be the executor of their own task.")
        self.executor_id = user_id
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    class Config:
        from_attributes = True
        extra = "forbid"