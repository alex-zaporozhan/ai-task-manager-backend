import asyncio
import logging
import sys
from decimal import Decimal
from sqlalchemy import text

from src.infrastructure.database.session import engine, AsyncSessionLocal
from src.infrastructure.database.models import Base
from src.infrastructure.repositories.order_repository import PostgresOrderRepository
from src.domain.entities import Order, Currency, OrderStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SystemIntegration")


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created.")


async def verify_connection():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection active and secure.")
        return True
    except Exception as e:
        logger.critical(f"Database connection failed: {e}")
        return False


async def main():
    logger.info("Starting System Integration Test...")

    if not await verify_connection():
        sys.exit(1)

    await init_models()

    try:
        async with AsyncSessionLocal() as session:
            repository = PostgresOrderRepository(session)

            new_order = Order(
                title="Integration Test Order",
                description="Testing Postgres persistence via SQLAlchemy 2.0",
                client_email="architect@example.com",
                budget=Decimal("1500.00"),
                currency=Currency.USD,
                status=OrderStatus.NEW
            )

            logger.info(f"Attempting to save Order: {new_order.title}")
            saved_order = await repository.save(new_order)

            logger.info("Order saved successfully.")
            logger.info(f"Generated ID: {saved_order.id}")
            logger.info(f"Created At: {saved_order.created_at}")

            fetched_order = await repository.get_by_id(saved_order.id)
            if fetched_order:
                logger.info(f"Verification: Retrieved Order '{fetched_order.title}' from DB.")
            else:
                logger.error("Verification Failed: Order not found after save.")

    except Exception as e:
        logger.error(f"Integration failed with error: {e}")
        raise
    finally:
        await engine.dispose()
        logger.info("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())