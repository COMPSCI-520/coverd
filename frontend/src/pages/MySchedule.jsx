import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMySchedule } from "../api/mySchedule";
import { useAuth } from "../context/AuthContext";

function groupShiftsByWeek(shifts) {
  const grouped = {};

  shifts.forEach((shift) => {
    const date = new Date(shift.shift_date);

    const firstDay = new Date(date);

    firstDay.setDate(date.getDate() - date.getDay());

    const key = firstDay.toISOString().split("T")[0];

    if (!grouped[key]) {
      grouped[key] = [];
    }

    grouped[key].push(shift);
  });

  return grouped;
}

function getToken() {
  try {
    const raw = sessionStorage.getItem("coverd_auth");

    return raw ? JSON.parse(raw)?.access_token : null;
  } catch {
    return null;
  }
}


export default function MySchedule() {
  const navigate = useNavigate();

  const { user, logout } = useAuth();

  const token = getToken();

  function handleLogout() {
    logout();
    navigate("/");
  }

  const today = new Date();

  const [month, setMonth] = useState(today.getMonth() + 1);

  const [year, setYear] = useState(today.getFullYear());

  const [loading, setLoading] = useState(true);

  const [shifts, setShifts] = useState([]);

  const [error, setError] = useState("");

  useEffect(() => {
    async function loadSchedule() {
      if (!token) {
        setError("Please log in again.");
        setLoading(false);
        return;
      }
      try {
        setLoading(true);

        const data = await getMySchedule(token, month, year);

        setShifts(data.shifts);

        setError("");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadSchedule();
  }, [token, month, year]);

  const groupedShifts = useMemo(
    () => groupShiftsByWeek(shifts),
    [shifts]
  );

  return (
    <div className="wireframe-page">
      <main className="prototype-card dashboard-sized-card">
        <nav className="app-navbar">
          <div className="brand">coverd</div>

          <div className="app-tabs">
            <button onClick={() => navigate("/dashboard")}>
              Dashboard
            </button>

            <button onClick={() => navigate("/marketplace")}>
              Marketplace
            </button>

            <button className="selected">
              My Schedule
            </button>
          </div>

          <div className="nav-user">
              <div className="avatar-circle">
                {(user?.full_name || "Student")[0].toUpperCase()}
              </div>

              <span>{user?.full_name || "Student"}</span>

                <button onClick={handleLogout}>
                    Log out
                </button>
              </div>
        </nav>
        

        <section className="page-content compact-content">
          <div className="page-heading-row">
            <div>
              <h1>My Schedule</h1>

              <p>
                View your assigned shifts grouped by week.
              </p>
            </div>
          </div>

          <div className="filter-bar">
            <label>
              <span>Month</span>

              <select
                value={month}
                onChange={(e) => setMonth(Number(e.target.value))}
              >
                {Array.from({ length: 12 }, (_, i) => (
                  <option key={i + 1} value={i + 1}>
                    {new Date(0, i).toLocaleString("default", {
                      month: "long",
                    })}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Year</span>

              <select
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
              >
                {[2025, 2026, 2027].map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loading && (
            <div className="empty-state"
                style={{ padding: "2rem" }}
            >
              Loading schedule...
            </div>
          )}

          {error && (
            <div className="message error">
              {error}
            </div>
          )}

          {!loading &&
            !error &&
            Object.keys(groupedShifts).length === 0 && (
              <div className="empty-state" style={{ padding: "2rem" }}>
                No shifts scheduled for this month.
              </div>
            )}

          {!loading &&
            !error &&
            Object.entries(groupedShifts).map(
              ([week, weekShifts]) => (
                <div
                  className="table-card dashboard-table-card"
                  key={week}
                >
                  <div className="section-title-row">
                    <div className="section-title">
                      Week of{" "}
                      {new Date(week).toLocaleDateString("en-US", {
                        month: "long",
                        day: "numeric",
                        year: "numeric",
                        })}
                    </div>
                  </div>

                  <table className="marketplace-table compact-table">
                    <thead>
                      <tr>
                        <th>Day</th>
                        <th>Location</th>
                        <th>Time</th>
                        <th>Hours</th>
                        <th>Status</th>
                      </tr>
                    </thead>

                    <tbody>
                      {weekShifts.map((shift) => (
                        <tr key={shift.id}>
                          <td>{shift.day}</td>

                          <td>{shift.location}</td>

                          <td>
                            {shift.start_time} - {shift.end_time}
                          </td>

                          <td>{shift.hours}h</td>

                          <td>
                            <span className="status-pill status-available">
                              {shift.status === "assigned"
                                ? "Confirmed"
                                : shift.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )
            )}
        </section>
      </main>
    </div>
  );
}