import threading
import requests

BASE_URL = "http://localhost:8000"

STUDENT_1 = {
    "email": "student@coverd.dev",
    "password": "student123",
}

STUDENT_2 = {
    "email": "taylor@coverd.dev",
    "password": "student123",
}

SHIFT_ID = "6a01464e870b75c28884d7d2"


def login(credentials):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=credentials,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def claim_shift(name, token):
    response = requests.post(
        f"{BASE_URL}/marketplace/shifts/{SHIFT_ID}/claim",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    print(f"{name}: status={response.status_code}, body={response.text}")


def main():
    token_1 = login(STUDENT_1)
    token_2 = login(STUDENT_2)

    thread_1 = threading.Thread(target=claim_shift, args=("student-1", token_1))
    thread_2 = threading.Thread(target=claim_shift, args=("student-2", token_2))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()


if __name__ == "__main__":
    main()