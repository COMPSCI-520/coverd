# Coverd: UMass Shift Management System

## Project Overview

Coverd is a centralized shift management system for UMass dining commons student workers and managers. The project addresses problems caused by manually maintained Google Sheets and informal communication channels for student shift scheduling.

The main issues addressed by Coverd are:

- **Privacy:** Student schedules and availability should not be visible to the entire staff.
- **Shift coordination:** Students need a structured way to request shift drops and pick up available shifts.
- **Manager oversight:** Managers need one place to review and act on student shift requests.
- **International student compliance:** International students must stay within a 20-hour weekly work limit during the academic semester.

Coverd provides a student dashboard, shift marketplace, and manager dashboard to make shift scheduling more organized, trackable, and safer for compliance.

---

## Implemented Features

### Student Features

- Student login.
- Student dashboard with weekly shift information.
- Shift marketplace showing available shifts.
- Ability to pick up available shifts.
- Ability to request dropping an assigned shift.
- My Requests page to track pending, approved, and denied drop requests.
- International student weekly-hour warning.
- Backend compliance check to help prevent international students from exceeding the weekly 20-hour limit.

### Manager Features

- Manager login.
- Manager dashboard.
- View student shift requests.
- Filter requests by status:
  - Pending
  - Approved
  - Denied
  - All
- Approve drop requests.
- Deny drop requests.
- Approved drop requests release the shift back to the marketplace.

### Backend Features

- FastAPI backend.
- MongoDB database.
- JWT-based authentication.
- Role-based access for student and manager routes.
- Router/service/repository structure.
- Seed script for demo users and demo shift data.
- Health check endpoint.

### Frontend Features

- React frontend built with Vite.
- Login page.
- Student dashboard route.
- Manager dashboard route.
- Protected routes based on user role.
- API helper files for frontend-backend communication.

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- React Router

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- PyMongo
- MongoDB
- python-jose
- passlib / bcrypt

### Development Tools

- Docker
- Docker Compose
- Git / GitHub

---

## Repository Structure

~~~text
coverd/
├── backend/
│   ├── dependencies/          # Database and authentication dependencies
│   ├── models/                # Backend user/domain models
│   ├── repositories/          # MongoDB data access logic
│   ├── routers/               # FastAPI route definitions
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic
│   ├── main.py                # FastAPI application entry point
│   ├── seed.py                # Demo data seed script
│   ├── seed_fixtures.json     # Optional seed volume / options
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile             # Backend Docker build file
│
├── frontend/
│   ├── src/
│   │   ├── api/               # Frontend API helper functions
│   │   ├── context/           # Authentication context
│   │   ├── pages/             # Login, Student Dashboard, Manager Dashboard
│   │   ├── App.jsx            # Application routes
│   │   └── main.jsx           # React entry point
│   ├── package.json           # Frontend dependencies and scripts
│   ├── vite.config.js         # Vite configuration
│   └── Dockerfile             # Frontend Docker build file
│
├── docker-compose.yml         # Local Docker Compose setup
├── .env.example               # Example environment variables
└── README.md                  # Main project documentation
~~~

---

## Prerequisites

Install the following before running the project:

- Git
- Docker Desktop
- Docker Compose
- Node.js and npm, if running the frontend outside Docker
- Python 3.11+ if running the backend outside Docker

---

## Environment Variables

Create a `.env` file using `.env.example` as a reference.

Example:

~~~env
MONGO_URI=mongodb://mongo:27017/coverd
DATABASE_NAME=coverd
JWT_SECRET_KEY=change_this_to_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
~~~

For Docker Compose, the MongoDB URI should use the Docker service name:

~~~env
MONGO_URI=mongodb://mongo:27017/coverd
~~~

For running the backend directly on your machine, use:

~~~env
MONGO_URI=mongodb://localhost:27017/coverd
~~~

---

## Running the Full Project with Docker

From the project root:

~~~bash
docker compose up --build
~~~

This starts the local development services defined in `docker-compose.yml`.

Common local URLs:

~~~text
Frontend: http://localhost:5173
Backend API: http://localhost:8000
FastAPI Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/health
MongoDB: localhost:27017
~~~

To stop the project:

~~~bash
docker compose down
~~~

To stop the project and remove database volume data:

~~~bash
docker compose down -v
~~~

---

## Seeding Demo Data

The project includes a seed script that creates the main demo accounts, many generated student accounts (`student001@coverd.dev`, …), shifts for them, marketplace listings, and sample drop requests (pending / denied / approved). Optional tuning lives in `backend/seed_fixtures.json`.

After the containers are running, run:

~~~bash
docker compose exec backend python seed.py
~~~

The seed script creates these demo users:

~~~text
Student:
Email: student@coverd.dev
Password: student123

Manager:
Email: manager@coverd.dev
Password: manager123
~~~

Additional seeded students share the `bulk_student_password` from `backend/seed_fixtures.json` (default `student123`).

---

## Running the Backend Locally Without Docker

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

Start the backend:

~~~bash
uvicorn main:app --reload
~~~

The backend runs at:

~~~text
http://localhost:8000
~~~

FastAPI documentation is available at:

~~~text
http://localhost:8000/docs
~~~

---

## Running the Frontend Locally Without Docker

From the project root:

~~~bash
cd frontend
npm install
npm run dev
~~~

The frontend runs at:

~~~text
http://localhost:5173
~~~

The frontend expects the backend to run at:

~~~text
http://localhost:8000
~~~

If needed, create a `.env` file inside the `frontend/` folder:

~~~env
VITE_API_URL=http://localhost:8000
~~~

---

## Available Frontend Scripts

From the `frontend/` directory:

~~~bash
npm run dev
~~~

Starts the Vite development server.

~~~bash
npm run build
~~~

Creates a production build.

~~~bash
npm run lint
~~~

Runs ESLint.

~~~bash
npm run preview
~~~

Previews the production build locally.

---

## Main Backend Routes

When the backend is running, open:

~~~text
http://localhost:8000/docs
~~~

Important route groups include:

~~~text
/system
/auth
/students
/marketplace
/manager
~~~

Marketplace routes include:

~~~text
GET  /marketplace/shifts
POST /marketplace/shifts/{shift_id}/claim
POST /marketplace/shifts/{shift_id}/drop
~~~

Manager routes include:

~~~text
GET  /manager/requests
POST /manager/requests/{request_id}/approve
POST /manager/requests/{request_id}/deny
~~~

Student request tracking includes:

~~~text
GET /students/me/requests
~~~

---

## Manual Testing Checklist

### Student Flow

1. Start the project.
2. Seed demo data.
3. Open the frontend.
4. Log in as:

~~~text
student@coverd.dev
student123
~~~

5. Confirm the Student Dashboard loads.
6. Confirm assigned weekly shifts are visible.
7. Open the Marketplace tab.
8. Pick up an available shift.
9. Confirm success feedback appears.
10. Confirm the claimed shift is removed from the marketplace.
11. Request to drop an assigned shift.
12. Open the My Requests tab.
13. Confirm the request appears with pending/approved/denied status.

### Manager Flow

1. Log out from the student account.
2. Log in as:

~~~text
manager@coverd.dev
manager123
~~~

3. Confirm the Manager Dashboard opens.
4. Confirm pending requests are visible.
5. Approve a pending drop request.
6. Confirm the request is removed from the pending list.
7. Check the Approved tab or All tab.
8. Deny another request if available.
9. Confirm denied requests are visible in the Denied tab.

---

## Architecture Notes

The backend follows a layered structure:

- **Routers:** Define API endpoints.
- **Services:** Contain business logic.
- **Repositories:** Handle MongoDB queries and updates.
- **Schemas:** Define API request and response shapes.
- **Dependencies:** Provide shared authentication and database access.

This separation improves modularity, readability, and testability.

The frontend separates page-level UI from API helper functions. This keeps components focused on rendering and user interaction, while API files handle backend communication.

---

## Known Limitations and Future Work

- More automated tests should be added for backend services and frontend flows.
- Production CORS settings should be restricted instead of allowing all origins.
- More detailed manager schedule views can be added.
- More validation can be added for edge cases in shift approval workflows.
- Deployment configuration is currently focused on local development.

---

## Contributors

This project was developed as part of COMPSCI 520 Software Engineering at UMass Amherst.