import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await login(form.email, form.password);
      navigate("/");
    } catch {
      setError("Invalid email or password.");
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>IntelliMoney</h1>
        <p>Sign in to monitor spending, budgets, and your financial health score.</p>
        <form onSubmit={handleSubmit}>
          <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
          <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">Login</button>
        </form>
        <span>New here? <Link to="/register">Create an account</Link></span>
      </section>
    </main>
  );
}
