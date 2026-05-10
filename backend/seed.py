from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from pymongo import MongoClient

from config import settings
from services.auth_service import hash_password

FIXTURE_PATH = Path(__file__).resolve().parent / "seed_fixtures.json"

DEFAULT_OPTIONS: dict = {
    "generated_student_count": 40,
    "calendar_weeks": 5,
    "anchor_week_start": "2026-05-04",
    "bulk_student_password": "student123",
    "marketplace_post_count": 28,
    "pending_drop_count": 14,
    "denied_drop_count": 8,
    "approved_drop_count": 10,
}

CORE_USERS = [
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

LOCATIONS = [
    "Franklin Dining",
    "Berkshire DC",
    "Worcester DC",
    "Hampshire DC",
    "Hampshire Dining",
]

SLOT_TEMPLATES = [
    ("08:00", "12:00", 4.0),
    ("09:00", "13:00", 4.0),
    ("10:00", "15:00", 5.0),
    ("11:00", "15:00", 4.0),
    ("16:00", "20:00", 4.0),
    ("17:00", "21:00", 4.0),
    ("12:00", "19:30", 7.5),
]

FIRST_NAMES = (
    "Avery", "Blake", "Casey", "Drew", "Emery", "Finley", "Gray", "Harper",
    "Indigo", "Jamie", "Kai", "Logan", "Morgan", "Nico", "Oakley", "Parker",
    "Quinn", "Riley", "Sage", "Tatum", "Uriel", "Vesper", "Winter", "Alex",
    "Cameron", "Devon", "Ellis", "Frankie", "George", "Hayden", "Ira", "Jules",
)

LAST_NAMES = (
    "Ahmed", "Bennett", "Castro", "Diaz", "Esposito", "Frost", "Garcia", "Hayes",
    "Ibrahim", "Jensen", "Kowalski", "Lopez", "Martinez", "Nguyen", "Okonkwo",
    "Patel", "Quinn", "Reyes", "Singh", "Thompson", "Uwusu", "Vargas", "Walker",
    "Xu", "Young", "Zhang", "Adams", "Baker", "Cohen", "Dubois", "Ellington",
    "Fischer", "Griffin", "Holmes", "Inoue", "Johnson", "Kim", "Lee",
)


@dataclass
class SeededShift:
    doc: dict
    """If set, a shift_requests row is created for this shift after insert (same index)."""
    drop_request: dict | None = None


def _stable_seed(s: str) -> int:
    return sum(ord(c) for c in s)


def load_fixture_bundle() -> tuple[dict, list[dict]]:
    merged = dict(DEFAULT_OPTIONS)
    extra_users: list[dict] = []
    if not FIXTURE_PATH.is_file():
        return merged, extra_users
    try:
        raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return merged, extra_users
    opts = raw.get("options")
    if isinstance(opts, dict):
        merged.update(opts)
    au = raw.get("additional_users")
    if isinstance(au, list):
        extra_users = [u for u in au if isinstance(u, dict) and u.get("email")]
    return merged, extra_users


def build_demo_users(options: dict, extra_fixtures: list[dict] | None = None) -> list[dict]:
    domain = "coverd.dev"
    pwd = options["bulk_student_password"]
    count = int(options["generated_student_count"])
    users: list[dict] = list(CORE_USERS)
    core_emails = {u["email"] for u in CORE_USERS}
    for i in range(1, count + 1):
        email = f"student{i:03d}@{domain}"
        if email in core_emails:
            continue
        fn = FIRST_NAMES[i % len(FIRST_NAMES)]
        ln = LAST_NAMES[(i * 7) % len(LAST_NAMES)]
        users.append(
            {
                "email": email,
                "password": pwd,
                "role": "student",
                "full_name": f"{fn} {ln}",
                "is_international": i % 5 == 0,
            }
        )
    if extra_fixtures:
        by_email = {u["email"]: u for u in users}
        for u in extra_fixtures:
            by_email[u["email"]] = {
                "email": u["email"],
                "password": str(u.get("password", pwd)),
                "role": str(u.get("role", "student")),
                "full_name": str(u.get("full_name", u["email"].split("@")[0].title())),
                "is_international": bool(u.get("is_international", False)),
            }
        users = list(by_email.values())
    return users


def build_legacy_shift_specs(user_ids: dict[str, str]) -> list[SeededShift]:
    student_id = user_ids["student@coverd.dev"]
    taylor_id = user_ids["taylor@coverd.dev"]
    maya_id = user_ids["maya@coverd.dev"]

    return [
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Franklin Dining",
                "shift_date": "2026-05-04",
                "start_time": "09:00",
                "end_time": "13:00",
                "hours": 4.0,
                "status": "assigned",
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Berkshire DC",
                "shift_date": "2026-05-05",
                "start_time": "17:00",
                "end_time": "21:00",
                "hours": 4.0,
                "status": "assigned",
            },
            drop_request={
                "request_type": "drop",
                "requested_by": student_id,
                "status": "denied",
                "created_at": "2026-05-04T08:30:00Z",
                "reviewed_by": None,
                "reviewed_at": "2026-05-04T11:00:00Z",
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Worcester DC",
                "shift_date": "2026-05-06",
                "start_time": "10:00",
                "end_time": "15:00",
                "hours": 5.0,
                "status": "assigned",
            },
        ),
        SeededShift(
            doc={
                "student_id": None,
                "posted_by": taylor_id,
                "location": "Franklin Dining",
                "shift_date": "2026-05-07",
                "start_time": "10:00",
                "end_time": "13:00",
                "hours": 3.0,
                "status": "available",
            },
        ),
        SeededShift(
            doc={
                "student_id": None,
                "posted_by": maya_id,
                "location": "Berkshire DC",
                "shift_date": "2026-05-08",
                "start_time": "16:00",
                "end_time": "19:30",
                "hours": 3.5,
                "status": "available",
            },
        ),
        SeededShift(
            doc={
                "student_id": None,
                "posted_by": taylor_id,
                "location": "Hampshire DC",
                "shift_date": "2026-05-09",
                "start_time": "12:00",
                "end_time": "19:30",
                "hours": 7.5,
                "status": "available",
            },
        ),
        SeededShift(
            doc={
                "student_id": maya_id,
                "posted_by": maya_id,
                "location": "Worcester DC",
                "shift_date": "2026-05-10",
                "start_time": "08:00",
                "end_time": "11:00",
                "hours": 3.0,
                "status": "pending",
            },
            drop_request={
                "request_type": "drop",
                "requested_by": maya_id,
                "status": "pending",
                "created_at": "2026-05-05T10:00:00Z",
                "reviewed_by": None,
                "reviewed_at": None,
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Franklin Dining",
                "shift_date": "2026-06-08",
                "start_time": "08:00",
                "end_time": "12:00",
                "hours": 4.0,
                "status": "assigned",
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Berkshire DC",
                "shift_date": "2026-06-10",
                "start_time": "16:00",
                "end_time": "20:00",
                "hours": 4.0,
                "status": "assigned",
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Worcester DC",
                "shift_date": "2026-07-03",
                "start_time": "10:00",
                "end_time": "15:00",
                "hours": 5.0,
                "status": "assigned",
            },
        ),
        SeededShift(
            doc={
                "student_id": student_id,
                "posted_by": None,
                "location": "Hampshire Dining",
                "shift_date": "2026-07-15",
                "start_time": "12:00",
                "end_time": "17:00",
                "hours": 5.0,
                "status": "assigned",
            },
        ),
    ]


def _pick_week_days_fixed(seed: int, week_index: int, count: int) -> list[int]:
    days_used: list[int] = []
    for slot in range(count):
        d = (seed + week_index * 2 + slot * 3) % 7
        while d in days_used:
            d = (d + 1) % 7
        days_used.append(d)
    return days_used


def build_bulk_assigned_shifts(
    student_emails: list[str],
    user_ids: dict[str, str],
    options: dict,
) -> list[SeededShift]:
    anchor = date.fromisoformat(str(options["anchor_week_start"]))
    weeks = int(options["calendar_weeks"])
    out: list[SeededShift] = []
    for email in student_emails:
        sid = user_ids[email]
        seed = _stable_seed(email)
        for w in range(weeks):
            week_days = _pick_week_days_fixed(seed, w, 2)
            for slot_idx, day_offset in enumerate(week_days):
                shift_date = anchor + timedelta(weeks=w, days=day_offset)
                loc = LOCATIONS[(seed + w + slot_idx) % len(LOCATIONS)]
                start, end, hours = SLOT_TEMPLATES[(w + slot_idx) % len(SLOT_TEMPLATES)]
                out.append(
                    SeededShift(
                        doc={
                            "student_id": sid,
                            "posted_by": None,
                            "location": loc,
                            "shift_date": shift_date.isoformat(),
                            "start_time": start,
                            "end_time": end,
                            "hours": hours,
                            "status": "assigned",
                        }
                    )
                )
    return out


def build_marketplace_posts(
    student_emails: list[str],
    user_ids: dict[str, str],
    options: dict,
) -> list[SeededShift]:
    anchor = date.fromisoformat(str(options["anchor_week_start"]))
    weeks = int(options["calendar_weeks"])
    n = int(options["marketplace_post_count"])
    if not student_emails:
        return []
    out: list[SeededShift] = []
    for i in range(n):
        poster = student_emails[(i * 11) % len(student_emails)]
        pid = user_ids[poster]
        w = (i // 3) % max(weeks, 1)
        day = (i + w * 2) % 7
        shift_date = anchor + timedelta(weeks=w, days=day)
        slot_idx = i % len(SLOT_TEMPLATES)
        start, end, hours = SLOT_TEMPLATES[slot_idx]
        loc = LOCATIONS[i % len(LOCATIONS)]
        out.append(
            SeededShift(
                doc={
                    "student_id": None,
                    "posted_by": pid,
                    "location": loc,
                    "shift_date": shift_date.isoformat(),
                    "start_time": start,
                    "end_time": end,
                    "hours": hours,
                    "status": "available",
                }
            )
        )
    return out


def _collect_assigned_candidates(specs: list[SeededShift]) -> list[int]:
    return [
        i
        for i, s in enumerate(specs)
        if s.doc.get("status") == "assigned"
        and s.drop_request is None
        and s.doc.get("student_id") is not None
    ]


def attach_synthetic_drop_requests(
    specs: list[SeededShift],
    options: dict,
) -> None:
    pending_n = int(options["pending_drop_count"])
    denied_n = int(options["denied_drop_count"])
    approved_n = int(options["approved_drop_count"])

    assigned_idx = _collect_assigned_candidates(specs)
    cursor = 0

    def take(n: int) -> list[int]:
        nonlocal cursor
        out_i = []
        for _ in range(n):
            if cursor >= len(assigned_idx):
                break
            out_i.append(assigned_idx[cursor])
            cursor += 1
        return out_i

    for i in take(pending_n):
        s = specs[i]
        sid = s.doc["student_id"]
        s.doc["status"] = "pending"
        s.doc["posted_by"] = sid
        s.drop_request = {
            "request_type": "drop",
            "requested_by": sid,
            "status": "pending",
            "created_at": f"{s.doc['shift_date']}T14:00:00Z",
            "reviewed_by": None,
            "reviewed_at": None,
        }

    for i in take(denied_n):
        s = specs[i]
        sid = s.doc["student_id"]
        s.drop_request = {
            "request_type": "drop",
            "requested_by": sid,
            "status": "denied",
            "created_at": f"{s.doc['shift_date']}T09:15:00Z",
            "reviewed_by": None,
            "reviewed_at": f"{s.doc['shift_date']}T16:30:00Z",
        }

    for _ in range(approved_n):
        if cursor >= len(assigned_idx):
            break
        i = assigned_idx[cursor]
        cursor += 1
        s = specs[i]
        sid = s.doc["student_id"]
        s.doc["student_id"] = None
        s.doc["status"] = "available"
        s.doc["posted_by"] = sid
        s.drop_request = {
            "request_type": "drop",
            "requested_by": sid,
            "status": "approved",
            "created_at": f"{s.doc['shift_date']}T11:00:00Z",
            "reviewed_by": None,
            "reviewed_at": f"{s.doc['shift_date']}T11:45:00Z",
        }


_BULK_STUDENT_EMAIL = re.compile(r"^student\d{3}@coverd\.dev$")


def _student_emails_from_roster(demo_users: list[dict]) -> list[str]:
    return sorted(u["email"] for u in demo_users if u["role"] == "student")


def _bulk_only_emails(student_emails: list[str]) -> list[str]:
    return sorted(e for e in student_emails if _BULK_STUDENT_EMAIL.match(e))


def build_all_shift_specs(
    demo_users: list[dict],
    user_ids: dict[str, str],
    options: dict,
) -> list[SeededShift]:
    student_emails = _student_emails_from_roster(demo_users)
    bulk_emails = _bulk_only_emails(student_emails)
    legacy = build_legacy_shift_specs(user_ids)
    bulk = build_bulk_assigned_shifts(bulk_emails, user_ids, options)
    attach_synthetic_drop_requests(bulk, options)
    marketplace = build_marketplace_posts(student_emails, user_ids, options)
    return legacy + bulk + marketplace


def seed() -> None:
    options, fixture_users = load_fixture_bundle()
    demo_users = build_demo_users(options, fixture_users or None)

    client = MongoClient(settings.mongo_uri)
    db = client[settings.database_name]

    users = db["users"]
    shifts = db["shifts"]
    shift_requests = db["shift_requests"]

    user_ids: dict[str, str] = {}

    for user in demo_users:
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

    shifts.delete_many({})
    shift_requests.delete_many({})

    all_specs = build_all_shift_specs(demo_users, user_ids, options)
    shift_docs = [s.doc for s in all_specs]
    inserted_ids = list(shifts.insert_many(shift_docs).inserted_ids)

    request_docs: list[dict] = []
    for idx, spec in enumerate(all_specs):
        if spec.drop_request:
            request_docs.append({**spec.drop_request, "shift_id": str(inserted_ids[idx])})

    if request_docs:
        shift_requests.insert_many(request_docs)

    client.close()

    print("Dashboard and marketplace demo data seeded.")
    if FIXTURE_PATH.is_file():
        print(f"  ({FIXTURE_PATH.name} options merged)")
    print("Done.")


if __name__ == "__main__":
    seed()