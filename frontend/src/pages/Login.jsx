import { Navigate } from "react-router-dom";
import { SignIn } from "@clerk/clerk-react";

import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { clerkConfigured, clerkLoaded, isSignedIn } = useAuth();

  if (clerkConfigured && clerkLoaded && isSignedIn) {
    return <Navigate to="/app" replace />;
  }

  if (!clerkConfigured) {
    return (
      <div className="error">
        Authentication is not configured. Set VITE_CLERK_PUBLISHABLE_KEY in the
        frontend environment to enable Clerk sign-in.
      </div>
    );
  }

  return <SignIn routing="path" path="/login" signUpUrl="/register" />;
}