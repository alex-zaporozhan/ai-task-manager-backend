from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_current_user
from src.api.schemas import UserRegister, UserRead, Token, UserAdminUpdate
from src.core.security import get_password_hash, verify_password, create_access_token, create_password_reset_token
from src.domain.entities import User, UserRole
from src.infrastructure.database.models import UserModel, DepartmentModel
from src.infrastructure.repositories.user_repository import UserRepository
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication & Roles"])


class PasswordResetRequest(BaseModel):
    email: EmailStr


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
        user_data: UserRegister,
        session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user_repo = UserRepository(session)

    if await user_repo.get_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_data.department_id:
        dept_check = await session.execute(
            select(DepartmentModel).where(DepartmentModel.id == user_data.department_id)
        )
        if not dept_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Department not found")

    count_query = select(func.count()).select_from(UserModel)
    result = await session.execute(count_query)
    users_count = result.scalar_one()

    assigned_role = UserRole.ADMIN if users_count == 0 else UserRole.EMPLOYEE

    hashed_pw = get_password_hash(user_data.password)

    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
        department_id=user_data.department_id,
        role=assigned_role
    )
    return await user_repo.create(new_user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(
        request: PasswordResetRequest,
        session: Annotated[AsyncSession, Depends(get_db_session)]
):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_email(request.email)

    if user:
        token = create_password_reset_token(user.email)
        print(f"\n[EMAIL MOCK] Password Reset Link: http://localhost:8000/reset-password?token={token}\n")

    return {"message": "If the email exists, a reset link has been sent."}


@router.get("/me", response_model=UserRead)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.get("/users", response_model=List[UserRead])
async def list_all_users(
        session: Annotated[AsyncSession, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """Список всех пользователей (для Админа)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await session.execute(select(UserModel))
    models = result.scalars().all()

    # Ручной маппинг для надежности
    return [
        UserRead(
            id=m.id, email=m.email, full_name=m.full_name,
            role=UserRole(m.role), department_id=m.department_id,
            is_active=m.is_active, created_at=m.created_at
        ) for m in models
    ]


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user_admin(
        user_id: UUID,
        update_data: UserAdminUpdate,
        session: Annotated[AsyncSession, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Эндпоинт для управления пользователями (Role, Department, Name).
    Защищен логикой "Неприкосновенного Фаундера".
    """
    # 1. RBAC Check (Только админ может зайти сюда)
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can manage users")

    # 2. Поиск целевого пользователя (Target)
    query = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(query)
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. ЗАЩИТА ФАУНДЕРА (FOUNDER IMMUNITY)
    # Находим самого первого пользователя в системе
    first_user_query = select(UserModel).order_by(UserModel.created_at.asc()).limit(1)
    first_user_result = await session.execute(first_user_query)
    founder = first_user_result.scalar_one()

    # Если мы пытаемся редактировать Фаундера
    if target_user.id == founder.id:
        # Если я не сам Фаундер (другой админ пытается меня хакнуть)
        if current_user.id != founder.id:
            raise HTTPException(status_code=403, detail="You cannot modify the System Founder.")

        # Даже если я сам Фаундер, я не могу разжаловать себя (защита от дурака)
        if update_data.role is not None and update_data.role != UserRole.ADMIN:
            raise HTTPException(status_code=400, detail="Founder cannot change their own role.")

    # 4. Применение обновлений

    # Роль
    if update_data.role:
        target_user.role = update_data.role.value

    # Имя
    if update_data.full_name:
        target_user.full_name = update_data.full_name

    # Департамент (с проверкой существования)
    if update_data.department_id:
        dept_check = await session.execute(
            select(DepartmentModel).where(DepartmentModel.id == update_data.department_id)
        )
        if not dept_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"Department {update_data.department_id} does not exist")
        target_user.department_id = update_data.department_id

    await session.commit()
    await session.refresh(target_user)

    return UserRead.model_validate(target_user)