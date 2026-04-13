"""
Run once to populate the database with demo users for local development.

    python seed.py

Safe to re-run: existing users (matched by email) are skipped.
"""

from pymongo import MongoClient

from config import settings
from services.auth_service import hash_password

DEMO_USERS = [
    {
        "email": "student@coverd.dev",
        "password": "student123",
        "role": "student",
        "full_name": "Alex Student",
    },
    {
        "email": "manager@coverd.dev",
        "password": "manager123",
        "role": "manager",
        "full_name": "Jordan Manager",
    },
]


def seed():
    client = MongoClient(settings.mongo_uri)
    db = client[settings.database_name]
    collection = db["users"]

    for user in DEMO_USERS:
        if collection.find_one({"email": user["email"]}):
            print(f"  skipped  {user['email']} (already exists)")
            continue

        collection.insert_one(
            {
                "email": user["email"],
                "hashed_password": hash_password(user["password"]),
                "role": user["role"],
                "full_name": user["full_name"],
            }
        )
        print(f"  created  {user['email']}  ({user['role']})")

    client.close()
    print("Done.")


if __name__ == "__main__":
    seed()
