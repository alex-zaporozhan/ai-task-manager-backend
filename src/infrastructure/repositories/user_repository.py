from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities import User, UserRole
from src.infrastructure.database.models import UserModel

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            role=UserRole(model.role),
            is_active=model.is_active,
            department_id=model.department_id,
            created_at=model.created_at
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None

    async def create(self, user: User) -> User:
        # Убеждаемся, что ВСЕ поля из сущности переходят в модель БД
        user_model = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            role=user.role.value, # Конвертируем Enum в строку для БД
            is_active=user.is_active,
            department_id=user.department_id,
            created_at=user.created_at
        )
        self.session.add(user_model)
        await self.session.commit()
        # Повторно находим юзера, чтобы убедиться, что всё сохранилось верно
        return self._to_domain(user_model)