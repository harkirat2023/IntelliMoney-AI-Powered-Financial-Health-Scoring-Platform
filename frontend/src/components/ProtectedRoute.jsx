import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, loading, clerkConfigured } = useAuth();
  if (loading) return <div className="centered">Loading IntelliMoney...</div>;
  if (!user) return <Navigate to={clerkConfigured ? "/login" : "/connect-bank"} replace />;
  return children;
}