import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    monthly_income: 60000
  });
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      await register({ ...form, monthly_income: Number(form.monthly_income) });
      navigate("/app");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not create account. Try another email.");
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>Create your account</h1>
        <p>Start with your monthly income so IntelliMoney can estimate savings and score.</p>
        <form onSubmit={handleSubmit}>
          <label>Name<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
          <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label>
          <label>Password<input type="password" minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required /></label>
          <label>Monthly income<input type="number" value={form.monthly_income} onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">Register</button>
        </form>
        <span>Already registered? <Link to="/login">Login</Link></span>
        <div style={{ marginTop: "16px", padding: "12px", background: "#f0f9ff", borderRadius: "8px", fontSize: "0.9rem" }}>
          <strong>Demo Account:</strong><br />
          Email: demo@example.com<br />
          Password: password123
        </div>
      </section>
    </main>
  );
}
