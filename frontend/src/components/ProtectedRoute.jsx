import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="centered">Loading IntelliMoney...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_onboarded) return <Navigate to="/connect-bank" replace />;
  return children;
}
