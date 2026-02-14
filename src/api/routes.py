from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from uuid import UUID
from src.api.schemas import (
    TaskCreate, TaskRead, TaskAssign,
    CommentCreate, CommentRead, TaskStatusUpdate
)
from src.domain.entities import Task, User, Comment, TaskStatus
from src.api.dependencies import get_db_session, get_current_user
from src.infrastructure.repositories.task_repository import TaskRepository
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Вспомогательная функция для получения репозитория
async def get_task_repo(session: Annotated[AsyncSession, Depends(get_db_session)]) -> TaskRepository:
    return TaskRepository(session)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskCreate,
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """Создание задачи. Только авторизованные пользователи."""
    try:
        domain_entity = Task(
            owner_id=current_user.id,
            target_dept_id=task_data.target_dept_id or current_user.department_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            deadline=task_data.deadline
        )
    except (ValueError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    return await repository.save(domain_entity)


@router.get("/", response_model=List[TaskRead])
async def list_tasks(
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)],
        limit: int = 10,
        offset: int = 0
):
    """Список задач. Видимость зависит от роли (RBAC)."""
    return await repository.get_all(user=current_user, limit=limit, offset=offset)


@router.patch("/{task_id}/assign", response_model=TaskRead)
async def assign_executor(
        task_id: UUID,
        assign_data: TaskAssign,
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """Назначить исполнителя. Доступно только Админу или Владельцу задачи."""
    task = await repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверка прав: админ или автор
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to assign this task")

    try:
        # Вызываем логику из сущности Domain
        task.assign_executor(assign_data.executor_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return await repository.save(task)


@router.post("/{task_id}/comments", response_model=CommentRead)
async def add_comment(
        task_id: UUID,
        comment_data: CommentCreate,
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """Добавить комментарий (чат внутри задачи)."""
    task = await repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = Comment(
        task_id=task.id,
        author_id=current_user.id,
        text=comment_data.text
    )
    return await repository.add_comment(new_comment)


@router.get("/{task_id}/comments", response_model=List[CommentRead])
async def get_comments(
        task_id: UUID,
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """Получить историю чата."""
    return await repository.get_comments(task_id)


@router.post("/{task_id}/analyze")
async def analyze_task(
        task_id: UUID,
        repository: Annotated[TaskRepository, Depends(get_task_repo)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """AI-анализ задачи и всех комментариев к ней."""
    from src.infrastructure.services.ai_service import AIService

    task = await repository.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    comments = await repository.get_comments(task_id)
    ai = AIService()
    advice = await ai.analyze_task_context(task.title, task.description, comments)
    return {"task_id": task.id, "ai_advice": advice}