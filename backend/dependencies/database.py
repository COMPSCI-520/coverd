from typing import Generator

from pymongo import MongoClient
from pymongo.database import Database

from config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.database_name]


def get_db() -> Generator[Database, None, None]:
    yield db
