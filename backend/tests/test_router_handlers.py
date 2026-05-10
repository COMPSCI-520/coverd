from types import SimpleNamespace

from routers import auth as auth_router
from routers import manager as manager_router
from routers import marketplace as marketplace_router
from routers import student_dashboard as student_dashboard_router


class FakeRepo:
    def __init__(self, db):
        self.db = db


class FakeUser:
    def __init__(
        self,
        id="student-1",
        email="student@coverd.dev",
        role="student",
        full_name="Alex Student",
        is_international=True,
    ):
        self.id = id
        self.email = email
        self.role = role
        self.full_name = full_name
        self.is_international = is_international


def test_auth_login_returns_token_response(monkeypatch):
    fake_user = FakeUser(role="student")

    monkeypatch.setattr(auth_router, "authenticate", lambda email, password, db: fake_user)
    monkeypatch.setattr(auth_router, "create_access_token", lambda payload: "fake-token")

    body = SimpleNamespace(email="student@coverd.dev", password="student123")

    response = auth_router.login(body, db={})

    assert response.access_token == "fake-token"
    assert response.role == "student"
    assert response.full_name == "Alex Student"


def test_auth_me_returns_current_user_response():
    user = FakeUser()

    response = auth_router.me(current_user=user)

    assert response.id == "student-1"
    assert response.email == "student@coverd.dev"
    assert response.role == "student"
    assert response.full_name == "Alex Student"


def test_marketplace_get_shifts_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(marketplace_router, "MarketplaceRepository", FakeRepo)
    monkeypatch.setattr(
        marketplace_router,
        "list_available_shifts",
        lambda current_user, repo: {"shifts": [], "total": 0},
    )

    response = marketplace_router.get_marketplace_shifts(
        current_user=user,
        db={},
    )

    assert response == {"shifts": [], "total": 0}


def test_marketplace_claim_shift_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(marketplace_router, "MarketplaceRepository", FakeRepo)
    monkeypatch.setattr(
        marketplace_router,
        "claim_shift",
        lambda shift_id, current_user, repo: {
            "message": "Shift claimed successfully",
            "shift_id": shift_id,
        },
    )

    response = marketplace_router.claim_marketplace_shift(
        shift_id="shift-1",
        current_user=user,
        db={},
    )

    assert response["message"] == "Shift claimed successfully"
    assert response["shift_id"] == "shift-1"


def test_marketplace_drop_shift_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(marketplace_router, "MarketplaceRepository", FakeRepo)
    monkeypatch.setattr(
        marketplace_router,
        "request_drop",
        lambda shift_id, current_user, repo: {
            "message": "Drop request submitted for manager review",
            "shift_id": shift_id,
            "request_id": "request-1",
        },
    )

    response = marketplace_router.drop_shift(
        shift_id="shift-1",
        current_user=user,
        db={},
    )

    assert response["message"] == "Drop request submitted for manager review"
    assert response["shift_id"] == "shift-1"
    assert response["request_id"] == "request-1"


def test_student_dashboard_route_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(student_dashboard_router, "StudentDashboardRepository", FakeRepo)
    monkeypatch.setattr(
        student_dashboard_router,
        "get_student_dashboard",
        lambda current_user, repo: {"full_name": current_user.full_name},
    )

    response = student_dashboard_router.read_student_dashboard(
        current_user=user,
        db={},
    )

    assert response == {"full_name": "Alex Student"}


def test_student_requests_route_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(student_dashboard_router, "StudentDashboardRepository", FakeRepo)
    monkeypatch.setattr(
        student_dashboard_router,
        "get_student_requests",
        lambda current_user, repo: {"requests": [], "total": 0},
    )

    response = student_dashboard_router.read_student_requests(
        current_user=user,
        db={},
    )

    assert response == {"requests": [], "total": 0}


def test_student_schedule_route_calls_service(monkeypatch):
    user = FakeUser()

    monkeypatch.setattr(student_dashboard_router, "StudentDashboardRepository", FakeRepo)
    monkeypatch.setattr(
        student_dashboard_router,
        "get_student_month_schedule",
        lambda current_user, repo, month, year: {
            "month": month,
            "year": year,
            "shifts": [],
        },
    )

    response = student_dashboard_router.read_student_schedule(
        month=6,
        year=2026,
        current_user=user,
        db={},
    )

    assert response == {
        "month": 6,
        "year": 2026,
        "shifts": [],
    }


def test_manager_requests_route_calls_service(monkeypatch):
    manager = FakeUser(
        id="manager-1",
        email="manager@coverd.dev",
        role="manager",
        full_name="Jordan Manager",
        is_international=False,
    )

    monkeypatch.setattr(manager_router, "ManagerRepository", FakeRepo)
    monkeypatch.setattr(
        manager_router,
        "list_requests",
        lambda repo, status_filter=None: {
            "requests": [],
            "total": 0,
            "status_filter": status_filter,
        },
    )

    response = manager_router.get_all_requests(
        status="pending",
        current_user=manager,
        db={},
    )

    assert response["requests"] == []
    assert response["total"] == 0
    assert response["status_filter"] == "pending"


def test_manager_staff_schedule_route_calls_service(monkeypatch):
    manager = FakeUser(
        id="manager-1",
        email="manager@coverd.dev",
        role="manager",
        full_name="Jordan Manager",
        is_international=False,
    )

    monkeypatch.setattr(manager_router, "ManagerRepository", FakeRepo)
    monkeypatch.setattr(
        manager_router,
        "get_staff_schedule",
        lambda repo, week_start=None, schedule_date=None, view="week", location=None, student=None: {
            "week_start": week_start,
            "view": view,
            "location": location,
            "student": student,
            "staff": [],
        },
    )

    response = manager_router.read_staff_schedule(
        week_start="2026-06-08",
        schedule_date=None,
        view="week",
        location="Worcester DC",
        student="Alex",
        current_user=manager,
        db={},
    )

    assert response["week_start"] == "2026-06-08"
    assert response["view"] == "week"
    assert response["location"] == "Worcester DC"
    assert response["student"] == "Alex"
    assert response["staff"] == []


def test_manager_approve_request_route_calls_service(monkeypatch):
    manager = FakeUser(
        id="manager-1",
        email="manager@coverd.dev",
        role="manager",
        full_name="Jordan Manager",
        is_international=False,
    )

    monkeypatch.setattr(manager_router, "ManagerRepository", FakeRepo)
    monkeypatch.setattr(
        manager_router,
        "review_request",
        lambda request_id, action, current_user, repo: {
            "message": "Request approved successfully",
            "request_id": request_id,
            "action": action,
        },
    )

    response = manager_router.approve_request(
        request_id="request-1",
        current_user=manager,
        db={},
    )

    assert response["message"] == "Request approved successfully"
    assert response["request_id"] == "request-1"
    assert response["action"] == "approve"


def test_manager_deny_request_route_calls_service(monkeypatch):
    manager = FakeUser(
        id="manager-1",
        email="manager@coverd.dev",
        role="manager",
        full_name="Jordan Manager",
        is_international=False,
    )

    monkeypatch.setattr(manager_router, "ManagerRepository", FakeRepo)
    monkeypatch.setattr(
        manager_router,
        "review_request",
        lambda request_id, action, current_user, repo: {
            "message": "Request denied successfully",
            "request_id": request_id,
            "action": action,
        },
    )

    response = manager_router.deny_request(
        request_id="request-1",
        current_user=manager,
        db={},
    )

    assert response["message"] == "Request denied successfully"
    assert response["request_id"] == "request-1"
    assert response["action"] == "deny"