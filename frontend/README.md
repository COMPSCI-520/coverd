# Coverd Frontend

## Overview

The Coverd frontend is built with React and Vite. It provides the user interface for student workers and managers to interact with the Coverd backend.

The frontend includes:

- Login page
- Student Dashboard
- Shift Marketplace
- My Requests tab
- Manager Dashboard
- Role-based protected routes

---

## Frontend Tech Stack

- React
- Vite
- JavaScript
- React Router
- ESLint

---

## Frontend Folder Structure

~~~text
frontend/
├── src/
│   ├── api/                 # API helper functions
│   ├── context/             # Auth context
│   ├── pages/               # Login and dashboard pages
│   │   ├── LoginPage.jsx
│   │   ├── StudentDashboard.jsx
│   │   └── ManagerDashboard.jsx
│   ├── App.jsx              # Application routes
│   └── main.jsx             # React entry point
├── package.json             # Frontend dependencies and scripts
├── vite.config.js           # Vite dev server config
└── Dockerfile               # Frontend Docker build file
~~~

---

## Setup

From the project root:

~~~bash
cd frontend
npm install
~~~

Start the development server:

~~~bash
npm run dev
~~~

The frontend runs at:

~~~text
http://localhost:5173
~~~

---

## Running with Docker

From the project root:

~~~bash
docker compose up --build frontend
~~~

Usually, the full project should be started together:

~~~bash
docker compose up --build
~~~

---

## Environment Variables

Create a `.env` file inside the `frontend/` folder if needed:

~~~env
VITE_API_URL=http://localhost:8000
~~~

This tells the frontend where to send backend API requests.

---

## Available Scripts

~~~bash
npm run dev
~~~

Runs the Vite development server.

~~~bash
npm run build
~~~

Builds the app for production.

~~~bash
npm run lint
~~~

Runs ESLint.

~~~bash
npm run preview
~~~

Previews the production build locally.

---

## Application Routes

The frontend uses React Router.

~~~text
/            Login page
/dashboard   Student dashboard
/manager     Manager dashboard
~~~

The routes are protected by user role:

- students are sent to `/dashboard`,
- managers are sent to `/manager`,
- users without a valid session are sent back to `/`.

---

## Login Flow

After login, the frontend checks the user role returned by the backend.

- If the role is `student`, the user is redirected to `/dashboard`.
- If the role is `manager`, the user is redirected to `/manager`.

Demo accounts after seeding:

~~~text
Student:
Email: student@coverd.dev
Password: student123

Manager:
Email: manager@coverd.dev
Password: manager123
~~~

---

## Student Dashboard

The Student Dashboard supports:

- viewing weekly assigned shifts,
- viewing the international student warning,
- browsing available marketplace shifts,
- picking up available shifts,
- requesting to drop assigned shifts,
- tracking requests in the My Requests tab.

Student tabs include:

~~~text
Dashboard
Marketplace
My Requests
~~~

---

## Manager Dashboard

The Manager Dashboard supports:

- viewing student shift requests,
- filtering by request status,
- approving pending drop requests,
- denying pending drop requests,
- showing request status and shift details.

Manager tabs include:

~~~text
Pending
Approved
Denied
All
~~~

---

## API Helper Files

Frontend API helper files should be placed in:

~~~text
src/api/
~~~

Examples:

~~~text
src/api/auth.js
src/api/marketplace.js
src/api/manager.js
~~~

These files keep fetch logic separate from page components.

---

## Manual Testing Checklist

### Student UI

1. Start the backend and frontend.
2. Log in as the demo student.
3. Confirm the dashboard loads.
4. Confirm assigned shifts are shown.
5. Open Marketplace.
6. Pick up an available shift.
7. Confirm success or error feedback appears.
8. Request to drop an assigned shift.
9. Open My Requests.
10. Confirm the request appears with a status.

### Manager UI

1. Log in as the demo manager.
2. Confirm the Manager Dashboard opens.
3. Confirm pending requests are listed.
4. Approve a request.
5. Confirm success feedback appears.
6. Check approved/all request tabs.
7. Deny a request if available.
8. Confirm denied requests appear correctly.

---

## Development Notes

Keep page components focused on UI state and rendering. Put backend calls in `src/api/` files.

Use clear names for handlers such as:

~~~text
handleClaim
handleDrop
handleApprove
handleDeny
loadRequests
loadMarketplace
~~~

Add comments only when the logic is not obvious, such as when the UI refreshes data after a successful claim or approval.