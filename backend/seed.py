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
    {
        "email": "taylor@coverd.dev",
        "password": "student123",
        "role": "student",
        "full_name": "Taylor Kim",
        "is_international": False,
    },
    {
        "email": "maya@coverd.dev",
        "password": "student123",
        "role": "student",
        "full_name": "Maya Patel",
        "is_international": False,
    },
]


def seed():
    client = MongoClient(settings.mongo_uri)
    db = client[settings.database_name]

    users = db["users"]
    shifts = db["shifts"]
    shift_requests = db["shift_requests"]

    user_ids = {}

    for user in DEMO_USERS:
        existing_user = users.find_one({"email": user["email"]})

        user_doc = {
            "email": user["email"],
            "hashed_password": hash_password(user["password"]),
            "role": user["role"],
            "full_name": user["full_name"],
            "is_international": user["is_international"],
        }

        if existing_user:
            users.update_one({"_id": existing_user["_id"]}, {"$set": user_doc})
            user_ids[user["email"]] = str(existing_user["_id"])
            print(f"  updated  {user['email']} ({user['role']})")
        else:
            result = users.insert_one(user_doc)
            user_ids[user["email"]] = str(result.inserted_id)
            print(f"  created  {user['email']} ({user['role']})")

    student_id = user_ids["student@coverd.dev"]
    taylor_id = user_ids["taylor@coverd.dev"]
    maya_id = user_ids["maya@coverd.dev"]

    shifts.delete_many({})
    shift_requests.delete_many({})

    demo_shifts = [
        # Current student's assigned shifts: total 13 hours for the same week.
        {
            "student_id": student_id,
            "posted_by": None,
            "location": "Franklin Dining",
            "shift_date": "2026-05-04",
            "start_time": "09:00",
            "end_time": "13:00",
            "hours": 4.0,
            "status": "assigned",
        },
        {
            "student_id": student_id,
            "posted_by": None,
            "location": "Berkshire DC",
            "shift_date": "2026-05-05",
            "start_time": "17:00",
            "end_time": "21:00",
            "hours": 4.0,
            "status": "assigned",
        },
        {
            "student_id": student_id,
            "posted_by": None,
            "location": "Worcester DC",
            "shift_date": "2026-05-06",
            "start_time": "10:00",
            "end_time": "15:00",
            "hours": 5.0,
            "status": "assigned",
        },

        # Marketplace shifts.
        {
            "student_id": None,
            "posted_by": taylor_id,
            "location": "Franklin Dining",
            "shift_date": "2026-05-07",
            "start_time": "10:00",
            "end_time": "13:00",
            "hours": 3.0,
            "status": "available",
        },
        {
            "student_id": None,
            "posted_by": maya_id,
            "location": "Berkshire DC",
            "shift_date": "2026-05-08",
            "start_time": "16:00",
            "end_time": "19:30",
            "hours": 3.5,
            "status": "available",
        },
        {
            "student_id": None,
            "posted_by": taylor_id,
            "location": "Hampshire DC",
            "shift_date": "2026-05-09",
            "start_time": "12:00",
            "end_time": "19:30",
            "hours": 7.5,
            "status": "available",
        },
        {
            "student_id": maya_id,
            "posted_by": maya_id,
            "location": "Worcester DC",
            "shift_date": "2026-05-10",
            "start_time": "08:00",
            "end_time": "11:00",
            "hours": 3.0,
            "status": "pending",
        },
        {
            "student_id": str(student_id),
            "posted_by": None,
            "location": "Franklin Dining",
            "shift_date": "2026-06-08",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4,
            "status": "assigned",
        },
        {
            "student_id": str(student_id),
            "posted_by": None,
            "location": "Berkshire DC",
            "shift_date": "2026-06-10",
            "start_time": "16:00",
            "end_time": "20:00",
            "hours": 4,
            "status": "assigned",
        },
        {
            "student_id": str(student_id),
            "posted_by": None,
            "location": "Worcester DC",
            "shift_date": "2026-07-03",
            "start_time": "10:00",
            "end_time": "15:00",
            "hours": 5,
            "status": "assigned",
        },
        {
            "student_id": str(student_id),
            "posted_by": None,
            "location": "Hampshire Dining",
            "shift_date": "2026-07-15",
            "start_time": "12:00",
            "end_time": "17:00",
            "hours": 5,
            "status": "assigned",
        },
    ]

    inserted_shifts = list(shifts.insert_many(demo_shifts).inserted_ids)

    demo_requests = [
        {
            "shift_id": str(inserted_shifts[6]),
            "request_type": "drop",
            "requested_by": maya_id,
            "status": "pending",
            "created_at": "2026-05-05T10:00:00Z",
            "reviewed_by": None,
            "reviewed_at": None,
        },
        {
            "shift_id": str(inserted_shifts[1]),
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

    print("Dashboard and marketplace demo data seeded.")
    print("Done.")


if __name__ == "__main__":
    seed()