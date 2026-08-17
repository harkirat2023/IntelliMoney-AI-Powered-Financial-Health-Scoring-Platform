import { Link } from "react-router-dom";
import { SignIn } from "@clerk/clerk-react";

import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { clerkConfigured } = useAuth();

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>IntelliMoney</h1>
        <p>Sign in to monitor spending, budgets, and your financial health score.</p>
        {clerkConfigured ? (
          <SignIn
            routing="path"
            path="/login"
            signUpUrl="/register"
            fallbackRedirectUrl="/app"
          />
        ) : (
          <div className="error">
            Authentication is not configured. Set VITE_CLERK_PUBLISHABLE_KEY in the
            frontend environment to enable Clerk sign-in.
          </div>
        )}
        <span>New here? <Link to="/register">Create an account</Link></span>
      </section>
    </main>
  );
}