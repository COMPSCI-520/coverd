# Coverd Backend

## Overview

The Coverd backend is built with FastAPI and MongoDB. It provides APIs for authentication, student dashboard data, shift marketplace actions, student request tracking, and manager request review.

The backend is organized using a router-service-repository structure so that routing, business logic, and database logic are separated.

---

## Backend Tech Stack

- Python
- FastAPI
- Uvicorn
- MongoDB
- PyMongo
- Pydantic
- python-jose
- passlib / bcrypt
- python-dotenv

---

## Backend Folder Structure

~~~text
backend/
├── dependencies/          # Shared FastAPI dependencies
├── models/                # Backend user/domain models
├── repositories/          # MongoDB data access layer
├── routers/               # FastAPI route definitions
├── schemas/               # Pydantic request/response schemas
├── services/              # Business logic layer
├── main.py                # FastAPI application entry point
├── seed.py                # Demo data seed script
├── requirements.txt       # Python dependencies
└── Dockerfile             # Backend Docker build file
~~~

---

## Main Backend Components

### Routers

Routers define the HTTP API endpoints.

Main routers include:

~~~text
auth
student_dashboard
marketplace
manager
system
~~~

### Services

Services contain business rules, such as:

- checking whether a student can claim a shift,
- enforcing the international student 20-hour weekly limit,
- approving or denying shift requests,
- preparing dashboard response data.

### Repositories

Repositories handle MongoDB queries and updates. This keeps database logic separate from route handlers and service logic.

### Schemas

Schemas use Pydantic models to define API request and response shapes.

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

~~~env
MONGO_URI=mongodb://mongo:27017/coverd
DATABASE_NAME=coverd
JWT_SECRET_KEY=change_this_to_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
~~~

For local development without Docker, use:

~~~env
MONGO_URI=mongodb://localhost:27017/coverd
~~~

---

## Running Backend with Docker

From the project root:

~~~bash
docker compose up --build backend mongo
~~~

The backend runs at:

~~~text
http://localhost:8000
~~~

FastAPI docs are available at:

~~~text
http://localhost:8000/docs
~~~

Health check:

~~~text
http://localhost:8000/health
~~~

---

## Running Backend Locally Without Docker

From the project root:

~~~bash
cd backend
python -m venv .venv
~~~

Activate the virtual environment.

Windows PowerShell:

~~~bash
.venv\Scripts\Activate.ps1
~~~

macOS/Linux:

~~~bash
source .venv/bin/activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Run the backend:

~~~bash
uvicorn main:app --reload
~~~

---

## Seeding Demo Data

The seed script creates demo users, assigned shifts, available marketplace shifts, and sample shift requests.

If the backend container is already running:

~~~bash
docker compose exec backend python seed.py
~~~

Demo accounts:

~~~text
Student:
Email: student@coverd.dev
Password: student123

Manager:
Email: manager@coverd.dev
Password: manager123
~~~

---

## API Route Summary

### Health

~~~text
GET /health
~~~

Returns a basic backend health check.

### Student Dashboard

~~~text
GET /students/me/dashboard
GET /students/me/requests
~~~

Used by the student dashboard and My Requests tab.

### Marketplace

~~~text
GET  /marketplace/shifts
POST /marketplace/shifts/{shift_id}/claim
POST /marketplace/shifts/{shift_id}/drop
~~~

Used by students to view available shifts, claim shifts, and request to drop assigned shifts.

### Manager

~~~text
GET  /manager/requests
POST /manager/requests/{request_id}/approve
POST /manager/requests/{request_id}/deny
~~~

Used by managers to review and act on student shift requests.

---

## Important Business Rules

### International Student Limit

International students cannot exceed 20 scheduled work hours in a week. Before a shift is claimed, the backend checks the student’s assigned hours for that week and rejects the claim if the new total would exceed the limit.

### Atomic Shift Claiming

Shift claiming should only succeed if the shift is still available. The database update checks the shift status before assigning it, which helps prevent two students from claiming the same shift at the same time.

### Drop Requests

Students do not directly remove assigned shifts from their schedule. Instead, they submit a drop request. A manager must approve or deny the request.

When a manager approves a drop request, the shift becomes available in the marketplace again.

---

## Development Notes

The backend entry point is:

~~~text
main.py
~~~

FastAPI automatically generates interactive API documentation at:

~~~text
http://localhost:8000/docs
~~~

Use this page to inspect available endpoints and manually test backend behavior during development.

---

## Commenting Guidelines

Add comments for non-obvious logic, especially:

- weekly hour calculation,
- international student compliance,
- atomic claim updates,
- manager approval side effects,
- role-based access checks.

Avoid comments that simply repeat what the code already says.