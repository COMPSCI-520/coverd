import requests

BASE_URL = "http://localhost:8000"


def login(email, password):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def check(name, condition):
    print(f"{'PASS' if condition else 'FAIL'} - {name}")


student_token = login("student@coverd.dev", "student123")
manager_token = login("manager@coverd.dev", "manager123")

dashboard = requests.get(
    f"{BASE_URL}/students/me/dashboard",
    headers=auth(student_token),
    timeout=10,
)
check("Student dashboard loads", dashboard.status_code == 200)

marketplace = requests.get(
    f"{BASE_URL}/marketplace/shifts",
    headers=auth(student_token),
    timeout=10,
)
check("Marketplace loads", marketplace.status_code == 200)

staff_schedule = requests.get(
    f"{BASE_URL}/manager/staff-schedule?week_start=2026-05-11&view=week",
    headers=auth(manager_token),
    timeout=10,
)
check("Staff schedule loads", staff_schedule.status_code == 200)

student_manager_access = requests.get(
    f"{BASE_URL}/manager/requests",
    headers=auth(student_token),
    timeout=10,
)
check("Student blocked from manager route", student_manager_access.status_code == 403)

manager_requests = requests.get(
    f"{BASE_URL}/manager/requests",
    headers=auth(manager_token),
    timeout=10,
)
check("Manager requests load", manager_requests.status_code == 200)