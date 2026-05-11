# Coverd Testing and Evaluation Documentation

## Backend Unit Test Summary

Backend unit tests were implemented using Pytest to validate authentication logic, service-layer behavior, router access, model validation, marketplace workflows, manager workflows, and student dashboard functionality. These tests provide coverage for core backend logic before validating full system behavior.
The backend unit test suite achieved 91% coverage across the models, services, and routers modules.

## Integration and System Testing

API-based integration smoke testing was performed using `scripts/integration_smoke_test.py`.

The smoke test verified that the student dashboard API, marketplace API, manager staff schedule API, manager requests API, and student role restriction behavior all returned the expected responses.

Automated checks passed:
- Student dashboard loads
- Marketplace loads
- Staff schedule loads
- Student is blocked from manager routes
- Manager requests load

Manual browser-based integration testing was also performed to validate workflows that require UI interaction. Screenshots for manual integration testing are included in the final report appendix.

Manual workflows verified:
- Student login
- Student dashboard loading
- Marketplace loading
- Available shift claiming
- Pending/blocked shift claim prevention
- Drop request submission
- Student restriction from manager route
- Manager login
- Drop request approval
- Drop request denial
- Staff schedule loading
- Staff schedule filtering

All documented manual integration workflows passed during browser testing.

## Manual Browser Testing Summary

Student login was tested by signing in with the student demo account and confirming that the dashboard loaded successfully.

The student dashboard was tested by checking that weekly hours, upcoming shifts, pending requests, and this week’s shifts were displayed correctly.

The marketplace was tested by confirming that available and pending shifts loaded with the correct status labels and claim buttons.

The available shift claim workflow was tested by claiming an available shift and confirming that the shift was removed from the marketplace and reflected in the student dashboard.

Pending or blocked marketplace shifts were tested to confirm that they could not be claimed.

The drop request workflow was tested by requesting to drop an assigned student shift and confirming that the pending request count updated.

Student role restriction was tested by attempting to access a manager route while logged in as a student. The application redirected away from the protected manager page.

Manager login was tested by signing in with the manager demo account and confirming that the manager dashboard loaded.

Manager approval was tested by approving a pending drop request and confirming that the request status updated successfully.

Manager denial was tested by denying a pending drop request and confirming that the request moved to the denied state.

The staff schedule page was tested by loading the manager staff schedule and verifying that schedule data appeared.

Staff schedule filters were tested by applying date, view, location, and student filters and confirming that the displayed schedule updated based on the selected criteria.

## Concurrency Test Results

Concurrent shift claiming behavior was tested using simultaneous API requests from two student accounts.

Tested shift ID:
`6a01464e870b75c28884d7d2`

Observed results:
- Student 1 request returned `200 OK` with message: `"Shift claimed successfully"`
- Student 2 request returned `409 Conflict` with message: `"Shift was claimed by someone else just now. Please refresh."`

Expected behavior was that only one student should be able to successfully claim the shift while competing requests are rejected. The observed behavior matched the expected outcome, confirming that the backend prevents duplicate shift assignment under concurrent access conditions.

## Load/Performance Test Results

- Load testing was conducted against the GET /students/me/dashboard endpoint.
- The test simulated 50 total requests with 25 concurrent workers.
- All 50 requests completed successfully without application errors.
- The average response time was approximately 245.54 ms.
- The median response time was approximately 246.37 ms.
- The maximum observed response time was approximately 371.78 ms.
- The endpoint demonstrated stable behavior under repeated concurrent access during testing.


## Usability Testing

Manual usability evaluation was conducted during browser-based workflow testing. The main student and manager workflows were completed successfully using the existing UI.

Students were able to understand the dashboard, marketplace status labels, claim buttons, and drop request flow. Manager workflows for approving and denying requests were also clear. The staff schedule filters were usable and updated the displayed results as expected.

Feedback from testing suggested that success messages and status labels helped users understand workflow outcomes clearly.

## Testing Tools and Frameworks Used

- Pytest was used for backend unit and service-layer testing.
- pytest-cov was used to measure backend test coverage.
- FastAPI TestClient was used for backend router and API validation.
- The Requests library was used for API smoke testing, concurrency testing, and load testing.
- Docker Compose was used to run the full-stack integration environment locally.
- Manual browser testing was used to validate end-to-end student and manager workflows.
- Screenshots were captured as evidence for manual integration and workflow testing.

## Testing Limitations

The testing process focused primarily on integration, workflow validation, and non-functional evaluation appropriate for a course-scale full-stack application.

Large-scale production load testing, cross-browser compatibility testing, and automated end-to-end UI testing using tools such as Cypress or Selenium were not included due to project scope and time constraints.