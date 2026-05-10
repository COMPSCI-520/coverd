import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { claimShift, getAvailableShifts } from "../api/marketplace";
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

function StatusBadge({ status }) {
  const normalized = status?.toLowerCase();

  if (normalized === "available") {
    return <span className="status-pill status-available">Available</span>;
  }

  return <span className="status-pill status-pending">Pending</span>;
}

export default function ShiftMarketplace() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [shifts, setShifts] = useState([]);
  const [meta, setMeta] = useState({
    hours_this_week: 0,
    weekly_limit: 20,
    remaining_capacity: 0,
  });

  // Draft filters: user can type/select without instantly changing table.
  const [draftLocation, setDraftLocation] = useState("All locations");
  const [draftDate, setDraftDate] = useState("");
  const [draftMaxHours, setDraftMaxHours] = useState("");

  // Applied filters: table uses only these values.
  const [appliedLocation, setAppliedLocation] = useState("All locations");
  const [appliedDate, setAppliedDate] = useState("");
  const [appliedMaxHours, setAppliedMaxHours] = useState("");

  const [loading, setLoading] = useState(true);
  const [claimingId, setClaimingId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  async function loadMarketplace() {
    setLoading(true);
    setError(null);

    try {
      const response = await getAvailableShifts(getToken());
      setShifts(response.shifts ?? []);
      setMeta({
        hours_this_week: response.hours_this_week ?? 0,
        weekly_limit: response.weekly_limit ?? 20,
        remaining_capacity: response.remaining_capacity ?? 0,
      });
    } catch (err) {
      setError(err.message || "Could not load marketplace shifts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMarketplace();
  }, []);

  const locations = useMemo(() => {
    const unique = Array.from(new Set(shifts.map((shift) => shift.location)));
    return ["All locations", ...unique];
  }, [shifts]);

  const filteredShifts = useMemo(() => {
    return shifts.filter((shift) => {
      const matchesLocation =
        appliedLocation === "All locations" || shift.location === appliedLocation;

      const matchesDate = !appliedDate || shift.shift_date === appliedDate;

      const matchesHours =
        !appliedMaxHours || Number(shift.hours) <= Number(appliedMaxHours);

      return matchesLocation && matchesDate && matchesHours;
    });
  }, [shifts, appliedLocation, appliedDate, appliedMaxHours]);

  const firstBlockedShift = filteredShifts.find((shift) => shift.would_exceed_limit);

  function applyFilters() {
    setAppliedLocation(draftLocation);
    setAppliedDate(draftDate);
    setAppliedMaxHours(draftMaxHours);
  }

  async function handleClaim(shiftId) {
    setClaimingId(shiftId);
    setFeedback(null);

    try {
      await claimShift(getToken(), shiftId);
      setFeedback({
        type: "success",
        message: "Shift claimed successfully. It now appears in your dashboard.",
      });
      await loadMarketplace();
    } catch (err) {
      setFeedback({
        type: "error",
        message: err.message || "Could not claim this shift.",
      });
    } finally {
      setClaimingId(null);
    }
  }

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="wireframe-page">
      <main className="prototype-card">
        <nav className="app-navbar">
          <div className="brand">coverd</div>

          <div className="app-tabs">
              <button onClick={() => navigate("/dashboard")}>Dashboard</button>
              <button className="selected">Marketplace</button>
              <button onClick={() => navigate("/my-schedule")}>My Schedule</button>   
          </div>

          <div className="nav-user">
            <span>{user?.full_name || "Student"}</span>
            <button onClick={handleLogout}>Log out</button>
          </div>
        </nav>

        <section className="page-content">
          <div className="page-heading-row">
            <div>
              <h1>Shift Marketplace</h1>
              <p>
                Browse and claim available shifts
                {meta.remaining_capacity !== null &&
                  ` — Your remaining capacity: ${meta.remaining_capacity} hrs`}
              </p>
            </div>
          </div>

          <div className="filter-bar">
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
              <span>Date</span>
              <input
                type="date"
                value={draftDate}
                onChange={(event) => setDraftDate(event.target.value)}
              />
            </label>

            <label>
              <span>Max Hours</span>
              <input
                type="number"
                min="1"
                step="0.5"
                placeholder="Any"
                value={draftMaxHours}
                onChange={(event) => setDraftMaxHours(event.target.value)}
              />
            </label>

            <button className="primary-button" onClick={applyFilters}>
              Apply Filters
            </button>
          </div>

          {feedback && <div className={`message ${feedback.type}`}>{feedback.message}</div>}

          {error && <div className="message error">{error}</div>}

          <div className="table-card">
            {loading ? (
              <div className="empty-state">Loading marketplace shifts…</div>
            ) : filteredShifts.length === 0 ? (
              <div className="empty-state">No shifts match the selected filters.</div>
            ) : (
              <table className="marketplace-table">
                <thead>
                  <tr>
                    <th>Location</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Hours</th>
                    <th>Posted By</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>

                <tbody>
                  {filteredShifts.map((shift) => (
                    <tr key={shift.id}>
                      <td>{shift.location}</td>
                      <td>{formatDate(shift.shift_date)}</td>
                      <td>
                        {formatTime(shift.start_time)} – {formatTime(shift.end_time)}
                      </td>
                      <td>{shift.hours}h</td>
                      <td>{shift.posted_by || "—"}</td>
                      <td>
                        <StatusBadge status={shift.status} />
                      </td>
                      <td className="table-action">
                        <button
                          className="claim-button"
                          disabled={!shift.can_claim || claimingId === shift.id}
                          title={shift.claim_block_reason || ""}
                          onClick={() => handleClaim(shift.id)}
                        >
                          {claimingId === shift.id ? "Claiming…" : "Claim"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {firstBlockedShift && (
            <div className="warning-box">
              <strong>Compliance warning:</strong> {firstBlockedShift.claim_block_reason}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}