import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- 1. ИМПОРТЫ ПРОЕКТА ---
# Импортируем Base, чтобы Alembic видел все наши модели (User, Task, Department...)
from src.infrastructure.database.models import Base
# Импортируем URL, который мы загрузили из .env файла
from src.infrastructure.database.session import DATABASE_URL

# --- 2. КОНФИГУРАЦИЯ ---
config = context.config

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные для autogenerate
target_metadata = Base.metadata


# --- 3. ЛОГИКА МИГРАЦИЙ ---

def do_run_migrations(connection: Connection) -> None:
    """
    Эта функция запускается внутри async-контекста,
    но выполняет синхронные методы Alembic.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # compare_type=True заставляет Alembic замечать изменения типов колонок (String -> Integer)
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Запуск миграций в Online-режиме (с подключением к БД).
    """

    # 1. Получаем конфигурацию из alembic.ini в виде словаря
    configuration = config.get_section(config.config_ini_section) or {}

    # 2. ЖЕСТКО перезаписываем URL базы данных на тот, что в .env
    # Это гарантирует использование asyncpg, даже если в alembic.ini написано что-то другое
    configuration["sqlalchemy.url"] = DATABASE_URL

    # 3. Создаем асинхронный движок
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 4. Подключаемся и запускаем миграции
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_offline() -> None:
    """
    Запуск в Offline-режиме (генерация SQL-скрипта).
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Точка входа
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())