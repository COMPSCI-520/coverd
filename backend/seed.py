from pymongo import MongoClient

from config import settings
from services.auth_service import hash_password

DEMO_USERS = [
    {
        "email": "student@coverd.dev",
        "password": "student123",
        "role": "student",
        "full_name": "Alex Student",
        "is_international": True,
    },
    {
        "email": "manager@coverd.dev",
        "password": "manager123",
        "role": "manager",
        "full_name": "Jordan Manager",
        "is_international": False,
    },
]


def seed():
    client = MongoClient(settings.mongo_uri)
    db = client[settings.database_name]

    users = db["users"]
    shifts = db["shifts"]
    shift_requests = db["shift_requests"]

    student_id = None

    for user in DEMO_USERS:
        existing_user = users.find_one({"email": user["email"]})

        if existing_user:
            users.update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        "hashed_password": hash_password(user["password"]),
                        "role": user["role"],
                        "full_name": user["full_name"],
                        "is_international": user["is_international"],
                    }
                },
            )
            print(f"  updated  {user['email']} ({user['role']})")
            if user["role"] == "student":
                student_id = str(existing_user["_id"])
        else:
            result = users.insert_one(
                {
                    "email": user["email"],
                    "hashed_password": hash_password(user["password"]),
                    "role": user["role"],
                    "full_name": user["full_name"],
                    "is_international": user["is_international"],
                }
            )
            print(f"  created  {user['email']} ({user['role']})")
            if user["role"] == "student":
                student_id = str(result.inserted_id)

    if student_id is None:
        client.close()
        print("Student user not found. Seed aborted.")
        return

    shifts.delete_many({})
    shift_requests.delete_many({})

    demo_shifts = [
        {
            "student_id": student_id,
            "location": "Franklin Dining",
            "shift_date": "2026-05-06",
            "start_time": "09:00",
            "end_time": "12:00",
            "hours": 3.0,
            "status": "assigned",
        },
        {
            "student_id": student_id,
            "location": "Berkshire",
            "shift_date": "2026-05-08",
            "start_time": "17:00",
            "end_time": "21:00",
            "hours": 4.0,
            "status": "assigned",
        },
        {
            "student_id": student_id,
            "location": "Hampshire",
            "shift_date": "2026-05-14",
            "start_time": "11:00",
            "end_time": "14:30",
            "hours": 3.5,
            "status": "assigned",
        },
        {
            "student_id": None,
            "location": "Worcester",
            "shift_date": "2026-05-07",
            "start_time": "10:00",
            "end_time": "13:00",
            "hours": 3.0,
            "status": "available",
        },
        {
            "student_id": None,
            "location": "Franklin Dining",
            "shift_date": "2026-05-09",
            "start_time": "14:00",
            "end_time": "18:00",
            "hours": 4.0,
            "status": "available",
        },
    ]

    inserted_shifts = list(shifts.insert_many(demo_shifts).inserted_ids)

    demo_requests = [
        {
            "shift_id": str(inserted_shifts[1]),
            "request_type": "drop",
            "requested_by": student_id,
            "status": "pending",
            "created_at": "2026-05-05T10:00:00Z",
            "reviewed_by": None,
            "reviewed_at": None,
        },
        {
            "shift_id": str(inserted_shifts[0]),
            "request_type": "drop",
            "requested_by": student_id,
            "status": "denied",
            "created_at": "2026-05-04T08:30:00Z",
            "reviewed_by": None,
            "reviewed_at": "2026-05-04T11:00:00Z",
        },
    ]

    shift_requests.insert_many(demo_requests)

    client.close()
    print("Dashboard demo data seeded.")
    print("Done.")


if __name__ == "__main__":
    seed()