import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "http://localhost:8000"

LOGIN_BODY = {
    "email": "student@coverd.dev",
    "password": "student123",
}


def login():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=LOGIN_BODY,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def call_dashboard(token):
    start = time.perf_counter()

    response = requests.get(
        f"{BASE_URL}/students/me/dashboard",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000
    return response.status_code, elapsed_ms


def main():
    token = login()

    total_requests = 50
    concurrent_workers = 25

    results = []

    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        futures = [
            executor.submit(call_dashboard, token)
            for _ in range(total_requests)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    status_codes = [status for status, _ in results]
    response_times = [elapsed for _, elapsed in results]

    success_count = sum(1 for status in status_codes if status == 200)
    error_count = total_requests - success_count

    print(f"Total requests: {total_requests}")
    print(f"Concurrent workers: {concurrent_workers}")
    print(f"Successful responses: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Average response time: {statistics.mean(response_times):.2f} ms")
    print(f"Median response time: {statistics.median(response_times):.2f} ms")
    print(f"Max response time: {max(response_times):.2f} ms")


if __name__ == "__main__":
    main()