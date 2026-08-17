import { Link } from "react-router-dom";
import { SignUp } from "@clerk/clerk-react";

import { useAuth } from "../auth/AuthContext";

export default function Register() {
  const { clerkConfigured } = useAuth();

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>Create your account</h1>
        <p>Start with your monthly income so IntelliMoney can estimate savings and score.</p>
        {clerkConfigured ? (
          <SignUp
            routing="path"
            path="/register"
            signInUrl="/login"
            fallbackRedirectUrl="/app"
          />
        ) : (
          <div className="error">
            Authentication is not configured. Set VITE_CLERK_PUBLISHABLE_KEY in the
            frontend environment to enable Clerk sign-up.
          </div>
        )}
        <span>Already registered? <Link to="/login">Login</Link></span>
      </section>
    </main>
  );
}