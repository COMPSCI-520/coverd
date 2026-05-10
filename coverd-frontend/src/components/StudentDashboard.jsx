import { useState, useEffect } from "react";

const BASE_URL = "http://localhost:8000";

const token = () => localStorage.getItem("token");

const API = {
  getDashboard: async () => {
    const res = await fetch(`${BASE_URL}/students/me/dashboard`, {
      headers: {
        Authorization: `Bearer ${token()}`,
      },
    });

    if (res.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
      return null;
    }

    if (!res.ok) {
      throw new Error("Failed to load dashboard");
    }

    return res.json();
  },

  logout: () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  },
};

function StatusBadge({ status }) {
  const styles = {
    assigned: { label: "Assigned", bg: "#dcfce7", color: "#15803d" },
    confirmed: { label: "Confirmed", bg: "#dcfce7", color: "#15803d" },
    pending_drop: { label: "Pending drop", bg: "#fef9c3", color: "#92400e" },
    pending: { label: "Pending", bg: "#fef9c3", color: "#92400e" },
    approved: { label: "Approved", bg: "#dcfce7", color: "#15803d" },
    denied: { label: "Denied", bg: "#fee2e2", color: "#b91c1c" },
    available: { label: "Available", bg: "#dbeafe", color: "#1d4ed8" },
  };

  const s = styles[status?.toLowerCase()] || styles.pending;

  return (
    <span
      style={{
        background: s.bg,
        color: s.color,
        borderRadius: "9999px",
        padding: "3px 10px",
        fontSize: "12px",
        fontWeight: "600",
      }}
    >
      {s.label}
    </span>
  );
}

function Toast({ msg, type, onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div
      style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        zIndex: 999,
        background: type === "error" ? "#fef2f2" : "#f0fdf4",
        border: `1px solid ${type === "error" ? "#fca5a5" : "#86efac"}`,
        color: type === "error" ? "#b91c1c" : "#15803d",
        borderRadius: "10px",
        padding: "12px 18px",
        fontSize: "13px",
        fontWeight: "500",
        boxShadow: "0 4px 20px rgba(0,0,0,0.1)",
        maxWidth: "320px",
      }}
    >
      {msg}
    </div>
  );
}

function fmtTime(t) {
  if (!t) return "";
  const [h, m] = t.split(":").map(Number);
  const ampm = h >= 12 ? "PM" : "AM";
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${ampm}`;
}

function fmtDate(d) {
  if (!d) return "";
  const date = new Date(`${d}T00:00:00`);
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

function ShiftTable({ shifts }) {
  if (!shifts || shifts.length === 0) {
    return (
      <p style={{ color: "#6b7280", fontSize: "14px", padding: "20px" }}>
        No shifts to display.
      </p>
    );
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse" }}>
      <thead>
        <tr style={{ background: "#f9fafb" }}>
          {["Day", "Location", "Time", "Hours", "Status"].map((h) => (
            <th
              key={h}
              style={{
                padding: "10px 20px",
                textAlign: "left",
                fontSize: "11px",
                fontWeight: "600",
                color: "#6b7280",
                letterSpacing: "0.05em",
                textTransform: "uppercase",
                borderBottom: "1px solid #e5e7eb",
              }}
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {shifts.map((shift, i) => (
          <tr
            key={`${shift.shift_date}-${shift.start_time}-${i}`}
            style={{
              borderBottom:
                i < shifts.length - 1 ? "1px solid #f3f4f6" : "none",
            }}
          >
            <td
              style={{
                padding: "14px 20px",
                fontSize: "14px",
                fontWeight: "500",
                color: "#111",
              }}
            >
              {fmtDate(shift.shift_date)}
            </td>
            <td
              style={{
                padding: "14px 20px",
                fontSize: "14px",
                color: "#374151",
              }}
            >
              {shift.location}
            </td>
            <td
              style={{
                padding: "14px 20px",
                fontSize: "14px",
                color: "#374151",
              }}
            >
              {fmtTime(shift.start_time)} – {fmtTime(shift.end_time)}
            </td>
            <td
              style={{
                padding: "14px 20px",
                fontSize: "14px",
                color: "#374151",
              }}
            >
              {shift.hours}h
            </td>
            <td style={{ padding: "14px 20px" }}>
              <StatusBadge status={shift.status} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function Skeleton({ w = "100%", h = "20px", mb = "8px" }) {
  return (
    <div
      style={{
        width: w,
        height: h,
        background: "#e5e7eb",
        borderRadius: "6px",
        marginBottom: mb,
        animation: "pulse 1.5s ease-in-out infinite",
      }}
    />
  );
}

export default function StudentDashboard() {
  const [tab, setTab] = useState("dashboard");
  const [data, setData] = useState(null);
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const showToast = (msg, type = "success") => setToast({ msg, type });

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await API.getDashboard();
      if (res) {
        setData(res);
      }
    } catch (e) {
      setError("Could not load dashboard. Please check your connection or log in again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#f9fafb",
          fontFamily: "'Inter','Segoe UI',sans-serif",
        }}
      >
        <style>{pulse}</style>
        <nav style={navStyle}>
          <span
            style={{
              fontSize: "20px",
              fontWeight: "700",
              color: "#2563eb",
            }}
          >
            coverd
          </span>
        </nav>
        <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "32px 24px" }}>
          <Skeleton w="160px" h="28px" mb="24px" />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "16px",
              marginBottom: "20px",
            }}
          >
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                style={{
                  background: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "10px",
                  padding: "20px",
                }}
              >
                <Skeleton h="14px" mb="12px" />
                <Skeleton w="60px" h="28px" />
              </div>
            ))}
          </div>
          <div
            style={{
              background: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "10px",
              padding: "20px",
            }}
          >
            <Skeleton h="14px" mb="12px" />
            <Skeleton h="14px" mb="12px" />
            <Skeleton h="14px" mb="0" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#f9fafb",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'Inter','Segoe UI',sans-serif",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <p style={{ color: "#b91c1c", fontSize: "14px", marginBottom: "16px" }}>
            {error}
          </p>
          <button
            onClick={loadDashboard}
            style={{
              background: "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              padding: "9px 20px",
              fontSize: "13px",
              fontWeight: "600",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  const {
    full_name,
    is_international,
    hours_this_week,
    weekly_limit,
    remaining_hours,
    show_warning,
    warning_message,
    upcoming_shifts_count,
    next_shift,
    pending_requests_count,
    marketplace_available_count,
    weekly_shifts,
  } = data;

  const hoursPct =
    weekly_limit && weekly_limit > 0
      ? Math.min(hours_this_week / weekly_limit, 1)
      : 0;

  const initials = full_name
    ? full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "?";

  const navTabs = [
    { key: "dashboard", label: "Dashboard" },
    { key: "marketplace", label: "Marketplace" },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f9fafb",
        fontFamily: "'Inter','Segoe UI',sans-serif",
        color: "#111827",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * { box-sizing: border-box; }
        button { transition: opacity 0.15s; }
        button:hover { opacity: 0.85; }
        ${pulse}
      `}</style>

      <nav style={navStyle}>
        <span
          style={{
            fontSize: "20px",
            fontWeight: "700",
            color: "#2563eb",
            marginRight: "32px",
            letterSpacing: "-0.5px",
          }}
        >
          coverd
        </span>

        <div style={{ display: "flex", flex: 1 }}>
          {navTabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              style={{
                background: "none",
                border: "none",
                borderBottom:
                  tab === t.key ? "2px solid #2563eb" : "2px solid transparent",
                cursor: "pointer",
                fontFamily: "inherit",
                fontSize: "14px",
                fontWeight: tab === t.key ? "600" : "400",
                color: tab === t.key ? "#2563eb" : "#6b7280",
                padding: "0 20px",
                height: "56px",
                marginBottom: "-1px",
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "50%",
              background: "#dbeafe",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "12px",
              fontWeight: "700",
              color: "#1d4ed8",
            }}
          >
            {initials}
          </div>
          <span style={{ fontSize: "14px", color: "#374151" }}>{full_name}</span>
          <button
            onClick={API.logout}
            style={{
              marginLeft: "8px",
              background: "none",
              border: "1px solid #e5e7eb",
              borderRadius: "6px",
              padding: "4px 12px",
              fontSize: "12px",
              color: "#6b7280",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            Log out
          </button>
        </div>
      </nav>

      <div style={{ maxWidth: "1000px", margin: "0 auto", padding: "32px 24px" }}>
        {tab === "dashboard" && (
          <>
            <h1 style={{ fontSize: "22px", fontWeight: "700", margin: "0 0 24px" }}>
              Dashboard
            </h1>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: "16px",
                marginBottom: "20px",
              }}
            >
              <div style={card}>
                <div style={cardLabel}>Hours this week</div>
                <div
                  style={{
                    display: "flex",
                    alignItems: "baseline",
                    gap: "6px",
                    marginBottom: "12px",
                  }}
                >
                  <span style={{ fontSize: "28px", fontWeight: "700" }}>
                    {hours_this_week}
                  </span>
                  {weekly_limit ? (
                    <span style={{ fontSize: "14px", color: "#9ca3af" }}>
                      / {weekly_limit} hrs
                    </span>
                  ) : null}
                </div>

                {weekly_limit ? (
                  <>
                    <div
                      style={{
                        background: "#e5e7eb",
                        borderRadius: "999px",
                        height: "6px",
                        marginBottom: "8px",
                      }}
                    >
                      <div
                        style={{
                          background: hoursPct >= 0.9 ? "#ef4444" : "#2563eb",
                          borderRadius: "999px",
                          height: "100%",
                          width: `${hoursPct * 100}%`,
                        }}
                      />
                    </div>
                    <div style={{ fontSize: "12px", color: "#6b7280" }}>
                      {remaining_hours} hrs remaining
                    </div>
                  </>
                ) : (
                  <div style={{ fontSize: "12px", color: "#6b7280" }}>
                    No weekly hour limit applies
                  </div>
                )}
              </div>

              <div style={card}>
                <div style={cardLabel}>Upcoming shifts</div>
                <div style={{ fontSize: "28px", fontWeight: "700", marginBottom: "6px" }}>
                  {upcoming_shifts_count}
                </div>
                {next_shift && (
                  <div style={{ fontSize: "12px", color: "#6b7280" }}>
                    Next: {fmtDate(next_shift.shift_date)}, {fmtTime(next_shift.start_time)}
                  </div>
                )}
              </div>

              <div style={card}>
                <div style={cardLabel}>Pending requests</div>
                <div style={{ fontSize: "28px", fontWeight: "700", marginBottom: "6px" }}>
                  {pending_requests_count}
                </div>
                {pending_requests_count > 0 && (
                  <div style={{ fontSize: "12px", color: "#6b7280" }}>
                    Awaiting manager review
                  </div>
                )}
              </div>
            </div>

            {show_warning && (
              <div
                style={{
                  background: "#fffbeb",
                  border: "1px solid #fcd34d",
                  borderRadius: "8px",
                  padding: "12px 16px",
                  marginBottom: "20px",
                  display: "flex",
                  gap: "10px",
                  alignItems: "flex-start",
                }}
              >
                <span style={{ fontSize: "15px", flexShrink: 0 }}>⚠️</span>
                <p
                  style={{
                    margin: 0,
                    fontSize: "13px",
                    color: "#92400e",
                    lineHeight: "1.5",
                  }}
                >
                  <strong>International student limit:</strong> {warning_message}
                </p>
              </div>
            )}

            <div
              style={{
                background: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "10px",
                marginBottom: "20px",
              }}
            >
              <div
                style={{
                  padding: "16px 20px",
                  borderBottom: "1px solid #e5e7eb",
                }}
              >
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    color: "#6b7280",
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                  }}
                >
                  This week's shifts
                </span>
              </div>
              <ShiftTable shifts={weekly_shifts} />
            </div>

            <div
              style={{
                ...card,
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "center",
                display: "flex",
              }}
            >
              <div>
                <div style={{ fontSize: "15px", fontWeight: "600", marginBottom: "4px" }}>
                  Shift Marketplace
                </div>
                <div style={{ fontSize: "13px", color: "#6b7280" }}>
                  {marketplace_available_count} shifts available to pick up this week
                </div>
              </div>
              <button
                onClick={() => setTab("marketplace")}
                style={{
                  background: "#2563eb",
                  color: "#fff",
                  border: "none",
                  borderRadius: "8px",
                  padding: "9px 18px",
                  fontSize: "13px",
                  fontWeight: "600",
                  cursor: "pointer",
                  fontFamily: "inherit",
                }}
              >
                View Summary →
              </button>
            </div>
          </>
        )}

        {tab === "marketplace" && (
          <>
            <h1 style={{ fontSize: "22px", fontWeight: "700", margin: "0 0 6px" }}>
              Shift Marketplace
            </h1>
            <p style={{ fontSize: "14px", color: "#6b7280", margin: "0 0 20px" }}>
              Marketplace browsing and pickup flow is not integrated yet.
            </p>

            {show_warning && (
              <div
                style={{
                  background: "#fffbeb",
                  border: "1px solid #fcd34d",
                  borderRadius: "8px",
                  padding: "12px 16px",
                  marginBottom: "20px",
                  display: "flex",
                  gap: "10px",
                }}
              >
                <span>⚠️</span>
                <p style={{ margin: 0, fontSize: "13px", color: "#92400e" }}>
                  <strong>International student limit:</strong> {warning_message}
                </p>
              </div>
            )}

            <div style={card}>
              <div style={{ fontSize: "15px", fontWeight: "600", marginBottom: "8px" }}>
                Available shifts this week
              </div>
              <div style={{ fontSize: "28px", fontWeight: "700", marginBottom: "6px" }}>
                {marketplace_available_count}
              </div>
              <div style={{ fontSize: "13px", color: "#6b7280" }}>
                Full marketplace list and pickup actions can be connected once the
                marketplace backend endpoints are ready.
              </div>
            </div>
          </>
        )}
      </div>

      {toast && <Toast msg={toast.msg} type={toast.type} onClose={() => setToast(null)} />}
    </div>
  );
}

const navStyle = {
  background: "#fff",
  borderBottom: "1px solid #e5e7eb",
  padding: "0 32px",
  display: "flex",
  alignItems: "center",
  height: "56px",
  gap: "0",
  position: "sticky",
  top: 0,
  zIndex: 50,
};

const card = {
  background: "#fff",
  border: "1px solid #e5e7eb",
  borderRadius: "10px",
  padding: "20px 24px",
};

const cardLabel = {
  fontSize: "11px",
  fontWeight: "600",
  color: "#6b7280",
  letterSpacing: "0.06em",
  textTransform: "uppercase",
  marginBottom: "10px",
};

const pulse = `@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }`;