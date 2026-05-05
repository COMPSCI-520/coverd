import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getRequests, approveRequest, denyRequest } from "../api/manager";

const token = () => {
  try {
    const raw = sessionStorage.getItem("coverd_auth");
    if (!raw) return null;
    return JSON.parse(raw)?.access_token ?? null;
  } catch {
    return null;
  }
};

function fmtTime(t) {
  if (!t) return "";
  const [h, m] = t.split(":").map(Number);
  const ampm = h >= 12 ? "PM" : "AM";
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${ampm}`;
}

function fmtDate(d) {
  if (!d) return "";
  const date = new Date(`${d}T00:00:00`);
  return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
}

function fmtDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" }) +
    " at " + d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" });
}

function StatusBadge({ status }) {
  const map = {
    pending: { label: "Pending", bg: "#fef9c3", color: "#92400e" },
    approved: { label: "Approved", bg: "#dcfce7", color: "#15803d" },
    denied: { label: "Denied", bg: "#fee2e2", color: "#b91c1c" },
  };
  const s = map[status?.toLowerCase()] ?? map.pending;
  return (
    <span style={{
      background: s.bg, color: s.color, borderRadius: "9999px",
      padding: "3px 10px", fontSize: "12px", fontWeight: "600",
    }}>
      {s.label}
    </span>
  );
}

function TypeBadge({ type }) {
  return (
    <span style={{
      background: "#ede9fe", color: "#6d28d9", borderRadius: "9999px",
      padding: "3px 10px", fontSize: "12px", fontWeight: "600",
      textTransform: "capitalize",
    }}>
      {type}
    </span>
  );
}

function RequestCard({ req, onApprove, onDeny, actionState }) {
  const { shift } = req;
  const busy = actionState === req.id;
  const isPending = req.status === "pending";

  return (
    <div style={{
      background: "#fff",
      border: "1px solid #e5e7eb",
      borderRadius: "10px",
      padding: "20px 24px",
      display: "flex",
      gap: "20px",
      alignItems: "flex-start",
    }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px", flexWrap: "wrap" }}>
          <span style={{ fontWeight: "600", fontSize: "15px" }}>{req.student_name}</span>
          <TypeBadge type={req.request_type} />
          <StatusBadge status={req.status} />
        </div>

        {shift ? (
          <div style={{ fontSize: "13px", color: "#374151", marginBottom: "6px" }}>
            <span style={{ fontWeight: "500" }}>{shift.location}</span>
            &nbsp;&middot;&nbsp;{fmtDate(shift.shift_date)}
            &nbsp;&middot;&nbsp;{fmtTime(shift.start_time)} – {fmtTime(shift.end_time)}
            &nbsp;&middot;&nbsp;{shift.hours}h
          </div>
        ) : (
          <div style={{ fontSize: "13px", color: "#9ca3af", marginBottom: "6px" }}>Shift info unavailable</div>
        )}

        <div style={{ fontSize: "12px", color: "#9ca3af" }}>
          Submitted {fmtDateTime(req.created_at)}
          {req.reviewed_at && ` · Reviewed ${fmtDateTime(req.reviewed_at)}`}
        </div>
      </div>

      {isPending && (
        <div style={{ display: "flex", gap: "8px", flexShrink: 0, alignItems: "center" }}>
          <button
            onClick={() => onApprove(req.id)}
            disabled={busy}
            style={{
              background: busy ? "#e5e7eb" : "#16a34a",
              color: busy ? "#9ca3af" : "#fff",
              border: "none", borderRadius: "7px",
              padding: "7px 16px", fontSize: "13px", fontWeight: "600",
              cursor: busy ? "not-allowed" : "pointer", fontFamily: "inherit",
            }}
          >
            {busy ? "Saving…" : "Approve"}
          </button>
          <button
            onClick={() => onDeny(req.id)}
            disabled={busy}
            style={{
              background: "none",
              border: "1px solid #e5e7eb", borderRadius: "7px",
              padding: "7px 16px", fontSize: "13px", fontWeight: "600",
              color: busy ? "#9ca3af" : "#ef4444",
              cursor: busy ? "not-allowed" : "pointer", fontFamily: "inherit",
            }}
          >
            Deny
          </button>
        </div>
      )}
    </div>
  );
}

export default function ManagerDashboard() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab] = useState("pending");
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionState, setActionState] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const loadRequests = useCallback(async (statusFilter) => {
    setLoading(true);
    setError(null);
    try {
      const authToken = token();
      const res = await getRequests(authToken, statusFilter === "all" ? null : statusFilter);
      setRequests(res.requests ?? []);
    } catch {
      setError("Could not load requests. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRequests(tab);
  }, [tab, loadRequests]);

  function handleLogout() {
    logout();
    navigate("/");
  }

  async function handleApprove(requestId) {
    setActionState(requestId);
    setFeedback(null);
    try {
      await approveRequest(token(), requestId);
      setFeedback({ type: "success", message: "Drop request approved. Shift released to marketplace." });
      setRequests((prev) => prev.filter((r) => r.id !== requestId));
    } catch (err) {
      setFeedback({ type: "error", message: err.message });
    } finally {
      setActionState(null);
    }
  }

  async function handleDeny(requestId) {
    setActionState(requestId);
    setFeedback(null);
    try {
      await denyRequest(token(), requestId);
      setFeedback({ type: "success", message: "Request denied. Shift remains assigned to the student." });
      setRequests((prev) => prev.filter((r) => r.id !== requestId));
    } catch (err) {
      setFeedback({ type: "error", message: err.message });
    } finally {
      setActionState(null);
    }
  }

  const navTabs = [
    { key: "pending", label: "Pending" },
    { key: "approved", label: "Approved" },
    { key: "denied", label: "Denied" },
    { key: "all", label: "All" },
  ];

  const pendingCount = tab === "pending" ? requests.length : null;

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f9fafb",
      fontFamily: "'Inter','Segoe UI',sans-serif",
      color: "#111827",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        button { transition: opacity 0.15s; }
        button:hover:not(:disabled) { opacity: 0.85; }
      `}</style>

      <nav style={{
        background: "#fff",
        borderBottom: "1px solid #e5e7eb",
        padding: "0 32px",
        display: "flex",
        alignItems: "center",
        height: "56px",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}>
        <span style={{
          fontSize: "20px", fontWeight: "700", color: "#2563eb",
          marginRight: "32px", letterSpacing: "-0.5px",
        }}>
          coverd
        </span>

        <div style={{ display: "flex", flex: 1 }}>
          {navTabs.map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} style={{
              background: "none", border: "none",
              borderBottom: tab === t.key ? "2px solid #2563eb" : "2px solid transparent",
              cursor: "pointer", fontFamily: "inherit", fontSize: "14px",
              fontWeight: tab === t.key ? "600" : "400",
              color: tab === t.key ? "#2563eb" : "#6b7280",
              padding: "0 20px", height: "56px", marginBottom: "-1px",
            }}>
              {t.label}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{
            background: "#fef9c3", color: "#92400e", borderRadius: "9999px",
            padding: "2px 10px", fontSize: "12px", fontWeight: "600",
          }}>
            Manager
          </div>
          <button onClick={handleLogout} style={{
            background: "none", border: "1px solid #e5e7eb", borderRadius: "6px",
            padding: "4px 12px", fontSize: "12px", color: "#6b7280",
            cursor: "pointer", fontFamily: "inherit",
          }}>
            Log out
          </button>
        </div>
      </nav>

      <div style={{ maxWidth: "860px", margin: "0 auto", padding: "32px 24px" }}>
        <div style={{ marginBottom: "24px" }}>
          <h1 style={{ fontSize: "22px", fontWeight: "700", margin: "0 0 4px" }}>
            Shift Requests
          </h1>
          <p style={{ fontSize: "14px", color: "#6b7280", margin: 0 }}>
            Review and action drop requests submitted by students.
          </p>
        </div>

        {feedback && (
          <div style={{
            padding: "10px 14px", borderRadius: "8px", fontSize: "13px", marginBottom: "16px",
            background: feedback.type === "success" ? "#f0fdf4" : "#fff0f0",
            color: feedback.type === "success" ? "#15803d" : "#c0392b",
            border: `1px solid ${feedback.type === "success" ? "#bbf7d0" : "#f5c6cb"}`,
          }}>
            {feedback.message}
          </div>
        )}

        {loading && (
          <div style={{ color: "#6b7280", fontSize: "14px", padding: "40px", textAlign: "center" }}>
            Loading…
          </div>
        )}

        {error && (
          <div style={{
            padding: "12px 16px", borderRadius: "8px",
            background: "#fff0f0", color: "#c0392b", border: "1px solid #f5c6cb",
            fontSize: "13px", display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            {error}
            <button onClick={() => loadRequests(tab)} style={{
              background: "none", border: "none", color: "#2563eb",
              cursor: "pointer", fontSize: "13px", fontFamily: "inherit",
            }}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && requests.length === 0 && (
          <div style={{
            background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px",
            padding: "48px", textAlign: "center", color: "#6b7280", fontSize: "14px",
          }}>
            {tab === "pending"
              ? "No pending requests. All caught up!"
              : `No ${tab === "all" ? "" : tab + " "}requests to show.`}
          </div>
        )}

        {!loading && requests.length > 0 && (
          <>
            {tab === "pending" && pendingCount > 0 && (
              <p style={{ fontSize: "13px", color: "#6b7280", marginBottom: "12px" }}>
                {pendingCount} request{pendingCount !== 1 ? "s" : ""} awaiting review
              </p>
            )}
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {requests.map((req) => (
                <RequestCard
                  key={req.id}
                  req={req}
                  onApprove={handleApprove}
                  onDeny={handleDeny}
                  actionState={actionState}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
