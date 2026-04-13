import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginRequest } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await loginRequest(email, password);
      login(data);
      navigate("/dashboard");
    } catch {
      setError("Login failed. Check your email and password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.logo}>coverd</h1>
        <p style={styles.subtitle}>UMass Shift Management</p>

        <h2 style={styles.heading}>Sign In</h2>

        {error && <p style={styles.error}>{error}</p>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Email address</label>
          <input
            type="email"
            placeholder="student@umass.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
            required
          />

          <label style={styles.label}>Password</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            required
          />

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? "Signing in…" : "Sign In"}
          </button>
        </form>

        <p style={styles.footer}>
          Don&apos;t have an account? Contact your manager.
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    width: "100%",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f7ff",
    fontFamily: "Arial, sans-serif",
  },
  card: {
    width: "100%",
    maxWidth: "360px",
    background: "#fff",
    padding: "32px",
    borderRadius: "12px",
    boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
  },
  logo: {
    margin: 0,
    textAlign: "center",
    color: "#4a7ef8",
    fontSize: "2rem",
    fontWeight: "700",
  },
  subtitle: {
    textAlign: "center",
    color: "#777",
    marginTop: "6px",
    marginBottom: "24px",
    fontSize: "0.9rem",
  },
  heading: {
    marginBottom: "18px",
    fontSize: "1.3rem",
  },
  error: {
    background: "#fff0f0",
    color: "#c0392b",
    border: "1px solid #f5c6cb",
    borderRadius: "8px",
    padding: "10px 12px",
    fontSize: "0.9rem",
    marginBottom: "12px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  label: {
    fontSize: "0.9rem",
    fontWeight: "600",
  },
  input: {
    padding: "10px 12px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    fontSize: "1rem",
  },
  button: {
    marginTop: "10px",
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    background: "#4a7ef8",
    color: "#fff",
    fontSize: "1rem",
    fontWeight: "600",
    cursor: "pointer",
    opacity: 1,
  },
  footer: {
    marginTop: "16px",
    textAlign: "center",
    color: "#777",
    fontSize: "0.85rem",
  },
};
