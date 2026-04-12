# Yields a MongoDB client session for use as a FastAPI dependency.
import os
from typing import Generator

from pymongo import MongoClient
from pymongo.database import Database

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/coverd")
DATABASE_NAME = os.getenv("DATABASE_NAME", "coverd")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]


def get_db() -> Generator[Database, None, None]:
    """
    FastAPI dependency that provides the MongoDB database instance.
    """
    try:
        yield db
    finally:
        pass