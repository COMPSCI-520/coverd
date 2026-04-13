import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StudentDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <span style={styles.logo}>coverd</span>
        <button onClick={handleLogout} style={styles.logoutButton}>
          Log out
        </button>
      </header>

      <main style={styles.main}>
        <h1 style={styles.welcome}>
          Welcome, {user?.full_name ?? "Student"}
        </h1>
        <p style={styles.role}>Role: {user?.role}</p>

        <div style={styles.placeholder}>
          <p>Your shift dashboard will appear here.</p>
        </div>
      </main>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f4f7ff",
    fontFamily: "Arial, sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 32px",
    background: "#fff",
    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
  },
  logo: {
    color: "#4a7ef8",
    fontSize: "1.4rem",
    fontWeight: "700",
  },
  logoutButton: {
    padding: "8px 18px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    background: "#fff",
    cursor: "pointer",
    fontSize: "0.9rem",
    color: "#444",
  },
  main: {
    maxWidth: "800px",
    margin: "40px auto",
    padding: "0 24px",
  },
  welcome: {
    fontSize: "1.6rem",
    color: "#222",
    marginBottom: "4px",
  },
  role: {
    color: "#777",
    fontSize: "0.9rem",
    marginBottom: "32px",
    textTransform: "capitalize",
  },
  placeholder: {
    background: "#fff",
    borderRadius: "12px",
    padding: "40px",
    textAlign: "center",
    color: "#aaa",
    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
  },
};
