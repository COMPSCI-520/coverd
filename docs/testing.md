# Testing Documentation

## Backend Unit Test Summary

Backend unit tests were implemented using Pytest for service, repository, router, and model validation.

## Integration/System Testing

API-based integration smoke testing was performed using `scripts/integration_smoke_test.py`.

Automated checks passed:
- Student dashboard loads
- Marketplace loads
- Staff schedule loads
- Student is blocked from manager routes
- Manager requests load

Manual browser testing will be used for the remaining workflows that require UI interaction, such as claiming shifts, requesting drops, approving/denying requests, and checking filters.

## Concurrency Test Results

Concurrent shift claiming behavior was tested using simultaneous API requests from two student accounts.

Tested shift ID:
`6a01464e870b75c28884d7d2`

Observed results:

* Student 1 request returned `200 OK` with message: `"Shift claimed successfully"`
* Student 2 request returned `409 Conflict` with message: `"Shift was claimed by someone else just now. Please refresh."`

Expected behavior was that only one student should be able to successfully claim the shift while competing requests are rejected. The observed behavior matched the expected outcome, confirming that the backend prevents duplicate shift assignment under concurrent access conditions.


## Load/Performance Test Results

Total requests: 50 
Concurrent workers: 25 
Successful responses: 50 
Errors: 0 
Average response time: 245.54 ms 
Median response time: 246.37 ms 
Max response time: 371.78 ms

A basic load test was conducted against the student dashboard endpoint using 50 total requests and 25 concurrent workers. The endpoint returned successful responses without application errors, indicating that the backend can handle repeated concurrent dashboard requests under small course-project load.


## Usability Testing

| Participant | Tasks Completed | Feedback | Result |
| ----------- | --------------- | -------- | ------ |

## Testing Tools Used

| Tool               | Purpose                              |
| ------------------ | ------------------------------------ |
| Pytest             | Backend unit and integration testing |
| FastAPI TestClient | API integration validation           |
| Requests           | Concurrency and load testing         |
| Docker Compose     | Full-stack integration environment   |
| MongoDB            | Backend data persistence             |

## Testing Limitations

The testing process focused primarily on integration, workflow validation, and non-functional evaluation appropriate for a course-scale full-stack application.
