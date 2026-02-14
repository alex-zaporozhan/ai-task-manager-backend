import asyncio
from src.infrastructure.database.session import engine
from src.infrastructure.database.models import Base

async def init_db():
    async with engine.begin() as conn:
        # Эта команда скажет Постгресу: "Создай все таблицы, которые описаны в моделях"
        await conn.run_sync(Base.metadata.create_all)
    print("🚀 Таблицы созданы успешно!")

if __name__ == "__main__":
    asyncio.run(init_db())