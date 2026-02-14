from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user
from src.api.schemas import DepartmentCreate, DepartmentRead
from src.domain.entities import User, UserRole
from src.infrastructure.database.models import DepartmentModel

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_data: DepartmentCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Создание отдела. Только для ADMIN.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins can create departments"
        )

    # Проверка на уникальность имени
    existing = await session.execute(select(DepartmentModel).where(DepartmentModel.name == dept_data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Department already exists")

    new_dept = DepartmentModel(name=dept_data.name)
    session.add(new_dept)
    await session.commit()
    await session.refresh(new_dept)
    return new_dept

@router.get("/", response_model=List[DepartmentRead])
async def list_departments(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Список отделов. Доступен всем авторизованным пользователям.
    """
    query = select(DepartmentModel)
    result = await session.execute(query)
    return result.scalars().all()