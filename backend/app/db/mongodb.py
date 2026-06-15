from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, database
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.mongodb_db]
    await database.users.create_index("email", unique=True)
    await database.expenses.create_index([("user_id", 1), ("date", -1)])
    await database.budgets.create_index(
        [("user_id", 1), ("category", 1), ("month", 1), ("year", 1)],
        unique=True,
    )


async def close_mongo_connection() -> None:
    global client, database
    if client is not None:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("MongoDB is not connected")
    return database
