import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { requestDrop } from "../api/marketplace";
import { useAuth } from "../context/AuthContext";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const SESSION_KEY = "coverd_auth";

function getToken() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw)?.access_token : null;
  } catch {
    return null;
  }
}

async function getDashboard() {
  const response = await fetch(`${BASE_URL}/students/me/dashboard`, {
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to load dashboard");
  }

  return response.json();
}

function formatDate(dateString) {
  if (!dateString) return "—";

  return new Date(`${dateString}T00:00:00`).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function formatTime(timeString) {
  if (!timeString) return "—";

  const [hour, minute] = timeString.split(":").map(Number);
  const suffix = hour >= 12 ? "PM" : "AM";

  return `${hour % 12 || 12}:${String(minute).padStart(2, "0")} ${suffix}`;
}

function isPastShift(shiftDate, endTime) {
  if (!shiftDate || !endTime) return false;

  const shiftEnd = new Date(`${shiftDate}T${endTime}:00`);
  const now = new Date();

  return shiftEnd < now;
}

function getInitials(name) {
  if (!name) return "AS";

  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function StatusBadge({ status }) {
  const normalized = status?.toLowerCase();

  if (normalized === "assigned") {
    return <span className="status-pill status-available">Confirmed</span>;
  }

  if (normalized === "pending") {
    return <span className="status-pill status-pending">Pending drop</span>;
  }

  return <span className="status-pill status-pending">{status}</span>;
}

export default function StudentDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [droppingId, setDroppingId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  async function loadDashboard() {
    setLoading(true);
    setError(null);

    try {
      const response = await getDashboard();
      setData(response);
    } catch {
      setError("Could not load dashboard. Please log in again or retry.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  async function handleDrop(shiftId) {
    setDroppingId(shiftId);
    setFeedback(null);

    try {
      await requestDrop(getToken(), shiftId);

      setFeedback({
        type: "success",
        message: "Drop request submitted. Awaiting manager approval.",
      });

      await loadDashboard();
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.message || "Could not submit drop request.",
      });
    } finally {
      setDroppingId(null);
    }
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  if (loading) {
    return (
      <div className="wireframe-page">
        <main className="prototype-card dashboard-sized-card">
          <nav className="app-navbar">
            <div className="brand">coverd</div>
          </nav>

          <section className="page-content compact-content">
            <div className="empty-state">Loading dashboard…</div>
          </section>
        </main>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="wireframe-page">
        <main className="prototype-card dashboard-sized-card">
          <section className="page-content compact-content">
            <div className="message error">{error}</div>

            <button className="primary-button" onClick={loadDashboard}>
              Retry
            </button>
          </section>
        </main>
      </div>
    );
  }

  const hoursPct =
    data.weekly_limit && data.weekly_limit > 0
      ? Math.min((data.hours_this_week / data.weekly_limit) * 100, 100)
      : 0;

  const displayName = user?.full_name || data.full_name || "Alex Student";

  return (
    <div className="wireframe-page">
      <main className="prototype-card dashboard-sized-card">
        <nav className="app-navbar">
          <div className="brand">coverd</div>

          <div className="app-tabs">
            <button className="selected">Dashboard</button>
            <button onClick={() => navigate("/marketplace")}>Marketplace</button>
          </div>

          <div className="nav-user">
            <span className="avatar">{getInitials(displayName)}</span>
            <span>{displayName}</span>
            <button onClick={handleLogout}>Log out</button>
          </div>
        </nav>

        <section className="page-content compact-content">
          <div className="dashboard-title">Dashboard</div>

          {feedback && (
            <div className={`message ${feedback.type}`}>
              {feedback.message}
            </div>
          )}

          <div className="summary-grid dashboard-summary-grid">
            <div className="summary-card">
              <span>Hours this week</span>
              <strong>
                {data.hours_this_week}
                {data.weekly_limit ? ` / ${data.weekly_limit}` : ""} hrs
              </strong>

              {data.weekly_limit && (
                <>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: `${hoursPct}%` }}
                    />
                  </div>

                  <small>{data.remaining_hours} hrs remaining</small>
                </>
              )}
            </div>

            <div className="summary-card">
              <span>Upcoming shifts</span>
              <strong>{data.upcoming_shifts_count}</strong>

              <small>
                {data.next_shift
                  ? `Next: ${formatDate(data.next_shift.shift_date)}, ${formatTime(
                      data.next_shift.start_time
                    )}`
                  : "No upcoming shifts"}
              </small>
            </div>

            <div className="summary-card">
              <span>Pending requests</span>
              <strong>{data.pending_requests_count}</strong>
              <small>Drop request — awaiting manager</small>
            </div>
          </div>

          {data.show_warning && (
            <div className="warning-box dashboard-warning">
              <strong>International student limit:</strong> {data.warning_message}
            </div>
          )}

          <div className="table-card dashboard-table-card">
            <div className="section-title-row">
              <div className="section-title">This Week&apos;s Shifts</div>
            </div>

            {data.weekly_shifts.length === 0 ? (
              <div className="empty-state">No shifts scheduled this week.</div>
            ) : (
              <table className="marketplace-table compact-table">
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Location</th>
                    <th>Time</th>
                    <th>Hours</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>

                <tbody>
                  {data.weekly_shifts.map((shift) => {
                    const completed = isPastShift(
                      shift.shift_date,
                      shift.end_time
                    );

                    const disabled =
                      droppingId === shift.id ||
                      shift.status !== "assigned" ||
                      completed;

                    return (
                      <tr key={shift.id}>
                        <td>{formatDate(shift.shift_date)}</td>
                        <td>{shift.location}</td>
                        <td>
                          {formatTime(shift.start_time)} –{" "}
                          {formatTime(shift.end_time)}
                        </td>
                        <td>{shift.hours}h</td>
                        <td>
                          <StatusBadge status={shift.status} />
                        </td>

                        <td className="table-action">
                          <button
                            className="secondary-button"
                            disabled={disabled}
                            title={
                              completed
                                ? "This shift is already completed and cannot be dropped."
                                : ""
                            }
                            onClick={() => handleDrop(shift.id)}
                          >
                            {completed
                              ? "Completed"
                              : droppingId === shift.id
                                ? "Requesting…"
                                : "Drop"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>

          <div className="marketplace-cta-card">
            <div>
              <strong>Shift Marketplace</strong>
              <p>
                {data.marketplace_available_count} shifts available to pick up
                this week
              </p>
            </div>

            <button
              className="primary-button small-primary"
              onClick={() => navigate("/marketplace")}
            >
              Browse Shifts →
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}