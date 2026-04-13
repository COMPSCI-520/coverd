from typing import Literal

from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    role: Literal["student", "manager"]
    full_name: str

    @classmethod
    def from_mongo(cls, doc: dict) -> "User":
        return cls(id=str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"})
