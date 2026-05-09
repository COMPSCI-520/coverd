import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getStaffSchedule } from "../api/manager";
import { useAuth } from "../context/AuthContext";

const SESSION_KEY = "coverd_auth";

function getToken() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw)?.access_token : null;
  } catch {
    return null;
  }
}

function getMonday(date = new Date()) {
  const copy = new Date(date);
  const day = copy.getDay();
  const diff = copy.getDate() - day + (day === 0 ? -6 : 1);
  copy.setDate(diff);
  return copy.toISOString().slice(0, 10);
}

function getToday() {
  return new Date().toISOString().slice(0, 10);
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
  return shiftEnd < new Date();
}

function ShiftStatus({ shift }) {
  if (shift.has_pending_drop || shift.status === "pending") {
    return <span className="status-pill status-pending">Pending drop</span>;
  }

  if (isPastShift(shift.shift_date, shift.end_time)) {
    return <span className="status-pill status-muted">Completed</span>;
  }

  return <span className="status-pill status-available">Confirmed</span>;
}

function StaffCard({ employee, viewMode }) {
  const hoursLabel = employee.is_international
    ? `${employee.hours_this_week} / ${employee.weekly_limit} hrs ${
        viewMode === "today" ? "today" : "this week"
      }`
    : `${employee.hours_this_week} hrs ${viewMode === "today" ? "today" : "this week"}`;

  const progressPct =
    employee.is_international && employee.weekly_limit
      ? Math.min((employee.hours_this_week / employee.weekly_limit) * 100, 100)
      : 0;

  return (
    <article className="staff-card">
      <div className="staff-card-header">
        <div>
          <h2>{employee.full_name}</h2>
          <p>{employee.email}</p>
        </div>

        <div className="staff-meta">
          <span className="staff-type-pill">
            {employee.is_international ? "International Student" : "Domestic Student"}
          </span>
        </div>
      </div>

      <div className="staff-card-summary">
        <div>
          <strong>{hoursLabel}</strong>

          {employee.is_international && (
            <>
              <div className="progress-track staff-progress">
                <div className="progress-fill" style={{ width: `${progressPct}%` }} />
              </div>
              <small>{employee.remaining_hours} hrs remaining</small>
            </>
          )}
        </div>

        <div>
          <strong>
            {employee.shift_count} assigned shift{employee.shift_count !== 1 ? "s" : ""}
          </strong>
          <small>
            {employee.pending_drop_count} pending drop
            {employee.pending_drop_count !== 1 ? "s" : ""}
          </small>
        </div>
      </div>

      {employee.shifts.length === 0 ? (
        <div className="staff-empty-shifts">
          No shifts scheduled {viewMode === "today" ? "today." : "for this week."}
        </div>
      ) : (
        <table className="staff-shift-table">
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
            {employee.shifts.map((shift) => (
              <tr key={shift.id}>
                <td>{formatDate(shift.shift_date)}</td>
                <td>{shift.location}</td>
                <td>
                  {formatTime(shift.start_time)} – {formatTime(shift.end_time)}
                </td>
                <td>{shift.hours}h</td>
                <td>
                  <ShiftStatus shift={shift} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </article>
  );
}

function CoverageNeededCard({ shifts, viewMode }) {
  return (
    <section className="coverage-card">
      <div className="coverage-card-header">
        <div>
          <h2>Shifts Needing Coverage</h2>
          <p>
            {viewMode === "today"
              ? "Approved dropped shifts still unclaimed for selected date"
              : "Approved dropped shifts still unclaimed for selected week"}
          </p>
        </div>

        <span>{shifts.length}</span>
      </div>

      {shifts.length === 0 ? (
        <div className="coverage-empty">
          No approved drops are waiting for coverage
          {viewMode === "today" ? " today." : " this week."}
        </div>
      ) : (
        <div className="coverage-list">
          {shifts.map((shift) => (
            <div className="coverage-item" key={shift.id}>
              <strong>{shift.location}</strong>
              <span>
                {formatDate(shift.shift_date)} · {formatTime(shift.start_time)} –{" "}
                {formatTime(shift.end_time)} · {shift.hours}h
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default function StaffSchedule() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [draftViewMode, setDraftViewMode] = useState("week");
  const [draftWeekStart, setDraftWeekStart] = useState(getMonday());
  const [draftScheduleDate, setDraftScheduleDate] = useState(getToday());
  const [draftLocation, setDraftLocation] = useState("All locations");
  const [draftStudent, setDraftStudent] = useState("");

  const [filters, setFilters] = useState({
    viewMode: "week",
    weekStart: getMonday(),
    scheduleDate: getToday(),
    location: "All locations",
    student: "",
  });

  async function loadSchedule(activeFilters = filters) {
    setLoading(true);
    setError("");

    try {
      const response = await getStaffSchedule(getToken(), activeFilters);
      setData(response);
    } catch (err) {
      setError(err.message || "Could not load staff schedule.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSchedule(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const locations = useMemo(() => {
    if (!data) return ["All locations"];

    const unique = new Set();

    data.staff.forEach((employee) => {
      employee.shifts.forEach((shift) => unique.add(shift.location));
    });

    data.shifts_needing_coverage?.forEach((shift) => {
      unique.add(shift.location);
    });

    return ["All locations", ...Array.from(unique).sort()];
  }, [data]);

  function applyFilters() {
    setFilters({
      viewMode: draftViewMode,
      weekStart: draftWeekStart,
      scheduleDate: draftScheduleDate,
      location: draftLocation,
      student: draftStudent.trim(),
    });
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  const activeViewMode = filters.viewMode || "week";

  return (
    <div className="manager-page">
      <nav className="manager-navbar">
        <span className="manager-brand" onClick={() => navigate("/manager")}>
          coverd
        </span>

        <div className="manager-nav-tabs">
          <button onClick={() => navigate("/manager")}>Shift Requests</button>
          <button className="active">Staff Schedule</button>
        </div>

        <div className="manager-actions">
          <span className="manager-pill">Manager</span>
          <button className="manager-logout" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </nav>

      <main className="staff-schedule-shell">
        <section className="staff-page-heading">
          <div>
            <h1>Staff Schedule</h1>
            <p>View employee schedules, daily coverage, and weekly hour totals.</p>
          </div>
        </section>

        <section className="staff-filter-bar">
          <label>
            <span>View</span>
            <select
              value={draftViewMode}
              onChange={(event) => setDraftViewMode(event.target.value)}
            >
              <option value="week">Weekly View</option>
              <option value="today">Daily View</option>
            </select>
          </label>

          <label>
            <span>{draftViewMode === "today" ? "Date" : "Week Starting"}</span>
            <input
              type="date"
              value={draftViewMode === "today" ? draftScheduleDate : draftWeekStart}
              onChange={(event) => {
                if (draftViewMode === "today") {
                  setDraftScheduleDate(event.target.value);
                } else {
                  setDraftWeekStart(event.target.value);
                }
              }}
            />
          </label>

          <label>
            <span>Location</span>
            <select
              value={draftLocation}
              onChange={(event) => setDraftLocation(event.target.value)}
            >
              {locations.map((location) => (
                <option key={location}>{location}</option>
              ))}
            </select>
          </label>

          <label>
            <span>Student Name</span>
            <input
              type="text"
              placeholder="Search student"
              value={draftStudent}
              onChange={(event) => setDraftStudent(event.target.value)}
            />
          </label>

          <button className="primary-button" onClick={applyFilters}>
            Apply Filters
          </button>
        </section>

        {error && <div className="message error">{error}</div>}

        {data && (
          <>
            <section className="summary-grid staff-summary-grid">
              <div className="summary-card">
                <span>Total Staff</span>
                <strong>{data.total_staff}</strong>
                <small>
                  {activeViewMode === "today"
                    ? "Students working selected day"
                    : "Students in schedule view"}
                </small>
              </div>

              <div className="summary-card">
                <span>Scheduled Shifts</span>
                <strong>{data.scheduled_shifts}</strong>
                <small>
                  {activeViewMode === "today"
                    ? "Assigned or pending shifts for selected date"
                    : "Assigned or pending shifts"}
                </small>
              </div>

              <div className="summary-card">
                <span>Scheduled Hours</span>
                <strong>{data.scheduled_hours}</strong>
                <small>
                  {activeViewMode === "today"
                    ? formatDate(data.week_start)
                    : `Week of ${formatDate(data.week_start)} – ${formatDate(data.week_end)}`}
                </small>
              </div>

              <div className="summary-card">
                <span>Pending Drops</span>
                <strong>{data.pending_drops}</strong>
                <small>Requests awaiting review</small>
              </div>
            </section>

            <CoverageNeededCard
              shifts={data.shifts_needing_coverage ?? []}
              viewMode={activeViewMode}
            />

            <section className="staff-list">
              {loading ? (
                <div className="empty-state">Loading staff schedule…</div>
              ) : data.staff.length === 0 ? (
                <div className="empty-state">
                  No staff match the selected {activeViewMode === "today" ? "day" : "week"}.
                </div>
              ) : (
                data.staff.map((employee) => (
                  <StaffCard
                    key={employee.student_id}
                    employee={employee}
                    viewMode={activeViewMode}
                  />
                ))
              )}
            </section>
          </>
        )}

        {!data && loading && <div className="empty-state">Loading staff schedule…</div>}
      </main>
    </div>
  );
}