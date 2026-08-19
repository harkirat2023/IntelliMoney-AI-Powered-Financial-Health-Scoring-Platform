import AuthGate from "./AuthGate";

export default function ProtectedRoute({ children }) {
  return <AuthGate requireOnboarding>{children}</AuthGate>;
}