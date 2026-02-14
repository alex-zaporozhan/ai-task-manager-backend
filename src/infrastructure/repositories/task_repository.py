from uuid import UUID
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Task, TaskStatus, TaskPriority, User, UserRole, Comment
from src.infrastructure.database.models import TaskModel, CommentModel, UserModel


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: TaskModel) -> Task:
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            owner_id=model.owner_id,
            executor_id=model.executor_id,
            target_dept_id=model.target_dept_id,
            status=TaskStatus(model.status),
            priority=TaskPriority(model.priority),
            deadline=model.deadline,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _comment_to_domain(self, model: CommentModel) -> Comment:
        return Comment(
            id=model.id,
            task_id=model.task_id,
            author_id=model.author_id,
            text=model.text,
            created_at=model.created_at
        )

    async def save(self, task: Task) -> Task:
        task_model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            owner_id=task.owner_id,
            executor_id=task.executor_id,
            target_dept_id=task.target_dept_id,
            status=task.status.value,
            priority=task.priority.value,
            deadline=task.deadline,
            created_at=task.created_at,
            updated_at=task.updated_at
        )

        merged_task = await self.session.merge(task_model)
        await self.session.commit()

        # Refresh критичен для получения ID и дефолтных значений времени из БД
        await self.session.refresh(merged_task)

        return self._to_domain(merged_task)

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        query = select(TaskModel).where(TaskModel.id == task_id)
        result = await self.session.execute(query)
        task_model = result.scalar_one_or_none()
        return self._to_domain(task_model) if task_model else None

    async def get_all(
            self,
            user: User,
            limit: int,
            offset: int,
            status: Optional[TaskStatus] = None,
            priority: Optional[TaskPriority] = None,
            deadline_start: Optional[datetime] = None,
            deadline_end: Optional[datetime] = None
    ) -> List[Task]:
        query = select(TaskModel)

        # --- RBAC LOGIC ---
        if user.role == UserRole.ADMIN:
            # Админ видит всё
            pass
        elif user.role == UserRole.MANAGER:
            # Менеджер видит:
            # 1. Задачи, назначенные на его отдел (target_dept_id)
            # 2. Задачи, которые он создал сам (даже если они не в отделе)
            if user.department_id:
                query = query.where(
                    (TaskModel.target_dept_id == user.department_id) |
                    (TaskModel.owner_id == user.id)
                )
            else:
                # Менеджер без отдела видит только свои
                query = query.where(TaskModel.owner_id == user.id)
        else:  # EMPLOYEE
            # Сотрудник видит только:
            # 1. Задачи, где он Исполнитель
            # 2. Задачи, где он Автор
            query = query.where(
                (TaskModel.owner_id == user.id) |
                (TaskModel.executor_id == user.id)
            )

        # --- FILTERS ---
        if status:
            query = query.where(TaskModel.status == status.value)
        if priority:
            query = query.where(TaskModel.priority == priority.value)
        if deadline_start:
            query = query.where(TaskModel.deadline >= deadline_start)
        if deadline_end:
            query = query.where(TaskModel.deadline <= deadline_end)

        query = query.limit(limit).offset(offset).order_by(TaskModel.created_at.desc())

        result = await self.session.execute(query)
        return [self._to_domain(model) for model in result.scalars().all()]

    async def add_comment(self, comment: Comment) -> Comment:
        comment_model = CommentModel(
            id=comment.id,
            task_id=comment.task_id,
            author_id=comment.author_id,
            text=comment.text,
            created_at=comment.created_at
        )
        self.session.add(comment_model)
        await self.session.commit()

        # Обязательно обновляем модель после вставки
        await self.session.refresh(comment_model)

        return self._comment_to_domain(comment_model)

    async def get_comments(self, task_id: UUID) -> List[Comment]:
        query = select(CommentModel).where(CommentModel.task_id == task_id).order_by(CommentModel.created_at.asc())
        result = await self.session.execute(query)
        return [self._comment_to_domain(model) for model in result.scalars().all()]