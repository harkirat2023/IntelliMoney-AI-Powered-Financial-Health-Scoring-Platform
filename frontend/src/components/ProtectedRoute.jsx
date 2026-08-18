import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, loading, clerkConfigured, isSignedIn, logout, refreshUser } = useAuth();

  if (loading) return <div className="centered">Loading IntelliMoney...</div>;

  if (!isSignedIn) {
    return <Navigate to={clerkConfigured ? "/login" : "/connect-bank"} replace />;
  }

  if (!user) {
    return (
      <div className="centered" style={{ textAlign: "center", padding: "3rem 1rem", maxWidth: 420 }}>
        <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "0.5rem" }}>
          We couldn't load your account
        </h2>
        <p style={{ color: "#94a3b8", marginBottom: "1.25rem" }}>
          Your session is active, but the account sync failed. Please try again in a moment.
        </p>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
          <button
            type="button"
            onClick={() => refreshUser()}
            style={{
              padding: "0.5rem 1.25rem",
              borderRadius: 8,
              border: "none",
              background: "#6366f1",
              color: "#fff",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Retry
          </button>
          <button
            type="button"
            onClick={() => logout()}
            style={{
              padding: "0.5rem 1.25rem",
              borderRadius: 8,
              border: "1px solid #334155",
              background: "transparent",
              color: "#cbd5e1",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Sign out
          </button>
        </div>
      </div>
    );
  }

  return children;
}