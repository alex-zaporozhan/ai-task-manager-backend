from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.entities import Task, TaskStatus

class ITaskRepository(ABC):
    """
    Интерфейс репозитория Задач.
    Определяет, какие методы должны быть у любого хранилища (Postgres, Mock и т.д.)
    """

    @abstractmethod
    async def save(self, task: Task) -> Task:
        pass

    @abstractmethod
    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        pass

    @abstractmethod
    async def get_all(
        self,
        user: any, # Тип User (из entities)
        limit: int,
        offset: int,
        status: Optional[TaskStatus] = None
    ) -> List[Task]:
        pass

    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        pass

    @abstractmethod
    async def add_comment(self, comment: any) -> any:
        pass

    @abstractmethod
    async def get_comments(self, task_id: UUID) -> List[any]:
        pass