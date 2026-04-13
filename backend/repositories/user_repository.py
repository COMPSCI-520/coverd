from bson import ObjectId
from pymongo.database import Database

from models.user import User


class UserRepository:
    def __init__(self, db: Database):
        self._collection = db["users"]

    def find_by_email(self, email: str) -> User | None:
        doc = self._collection.find_one({"email": email})
        if doc is None:
            return None
        return User.from_mongo(doc)

    def find_by_id(self, user_id: str) -> User | None:
        doc = self._collection.find_one({"_id": ObjectId(user_id)})
        if doc is None:
            return None
        return User.from_mongo(doc)
