from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConfigurationError, PyMongoError, ServerSelectionTimeoutError

from app.core.config import settings
from app.models import DOCUMENT_MODELS

mongodb_client: AsyncIOMotorClient | None = None
mongodb_database: AsyncIOMotorDatabase | None = None
database_ready = False
database_error: str | None = None


def get_database_status() -> dict[str, str | bool]:
    return {
        "ready": database_ready,
        "database": settings.mongodb_database,
        "error": database_error or "",
    }


async def init_database() -> bool:
    global mongodb_client, mongodb_database, database_ready, database_error

    if settings.mongodb_uri_has_placeholders:
        database_ready = False
        database_error = "MongoDB URI contains placeholder values. Update MONGODB_URI in .env."
        if settings.database_required:
            raise RuntimeError(database_error)
        return False

    try:
        from beanie import init_beanie

        mongodb_client = AsyncIOMotorClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=settings.mongodb_timeout_ms,
        )
        mongodb_database = mongodb_client[settings.mongodb_database]

        await mongodb_client.admin.command("ping")
        await init_beanie(database=mongodb_database, document_models=DOCUMENT_MODELS)

        database_ready = True
        database_error = None
        return True
    except (ConfigurationError, ServerSelectionTimeoutError, PyMongoError, RuntimeError) as exc:
        await close_database()
        database_ready = False
        database_error = str(exc)
        if settings.database_required:
            raise RuntimeError(f"MongoDB connection failed: {exc}") from exc
        return False


async def close_database() -> None:
    global mongodb_client, mongodb_database, database_ready

    if mongodb_client is not None:
        mongodb_client.close()

    mongodb_client = None
    mongodb_database = None
    database_ready = False


async def ping_database() -> dict[str, str | bool]:
    global database_ready, database_error

    if mongodb_client is None:
        await init_database()

    if mongodb_client is None:
        return get_database_status()

    try:
        await mongodb_client.admin.command("ping")
        database_ready = True
        database_error = None
    except PyMongoError as exc:
        database_ready = False
        database_error = str(exc)

    return get_database_status()


def get_database() -> AsyncIOMotorDatabase:
    if mongodb_database is None:
        raise RuntimeError("MongoDB is not initialized. Check /health/mongodb for details.")
    return mongodb_database
