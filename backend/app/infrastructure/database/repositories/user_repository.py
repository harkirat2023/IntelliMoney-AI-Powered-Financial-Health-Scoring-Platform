from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.utils.object_id import to_object_id


class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db

    async def get_by_id(self, user_id: str) -> User | None:
        doc = await self._db.users.find_one({"_id": to_object_id(user_id)})
        return User.from_mongo(doc) if doc else None

    async def get_by_email(self, email: str) -> User | None:
        doc = await self._db.users.find_one({"email": email})
        return User.from_mongo(doc) if doc else None

    async def create(self, user: User) -> User:
        doc = user.to_mongo()
        result = await self._db.users.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    async def update(self, user_id: str, data: dict) -> User | None:
        result = await self._db.users.update_one(
            {"_id": to_object_id(user_id)}, {"$set": data}
        )
        if result.modified_count == 0:
            return None
        return await self.get_by_id(user_id)
