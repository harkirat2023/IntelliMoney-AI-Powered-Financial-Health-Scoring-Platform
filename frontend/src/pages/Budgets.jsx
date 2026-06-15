import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";

import { api } from "../api/client";
import { currency } from "../utils/format";

const categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Travel", "Rent", "Other"];
const now = new Date();

export default function Budgets() {
  const [budgets, setBudgets] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [form, setForm] = useState({
    category: "Food",
    limit: "",
    month: now.getMonth() + 1,
    year: now.getFullYear()
  });
  const [error, setError] = useState("");

  async function load() {
    const [budgetResponse, statusResponse] = await Promise.all([
      api.get("/budgets"),
      api.get("/budgets/status")
    ]);
    setBudgets(budgetResponse.data);
    setStatuses(statusResponse.data);
  }

  useEffect(() => {
    load().catch(() => setError("Could not load budgets."));
  }, []);

  async function saveBudget(event) {
    event.preventDefault();
    setError("");
    try {
      await api.post("/budgets", { ...form, limit: Number(form.limit), month: Number(form.month), year: Number(form.year) });
      setForm({ ...form, limit: "" });
      await load();
    } catch {
      setError("Could not save budget. It may already exist for this month.");
    }
  }

  async function deleteBudget(id) {
    await api.delete(`/budgets/${id}`);
    await load();
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Budgets</h1>
          <p>Set category limits and monitor current month usage.</p>
        </div>
      </header>

      <section className="split">
        <form className="panel form-panel" onSubmit={saveBudget}>
          <h2>Create Budget</h2>
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {categories.map((category) => <option key={category}>{category}</option>)}
            </select>
          </label>
          <label>Monthly limit<input type="number" min="1" value={form.limit} onChange={(e) => setForm({ ...form, limit: e.target.value })} required /></label>
          <label>Month<input type="number" min="1" max="12" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })} required /></label>
          <label>Year<input type="number" min="2000" max="2100" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">Save Budget</button>
        </form>

        <article className="panel list-panel">
          <h2>Current Month Usage</h2>
          <div className="budget-list">
            {statuses.map((item) => (
              <div className={`budget-card ${item.state}`} key={item.id}>
                <div>
                  <strong>{item.category}</strong>
                  <span>{currency(item.spent)} of {currency(item.limit)}</span>
                </div>
                <div className="progress"><span style={{ width: `${Math.min(item.percentage_used, 100)}%` }} /></div>
                <small>{item.percentage_used}% used · {currency(item.remaining)} remaining</small>
              </div>
            ))}
            {!statuses.length && <p className="muted">Create budgets for the current month to see usage.</p>}
          </div>
        </article>
      </section>

      <section className="panel">
        <h2>All Budgets</h2>
        <div className="table">
          {budgets.map((budget) => (
            <div className="table-row" key={budget.id}>
              <span>{budget.category}<small>{budget.month}/{budget.year}</small></span>
              <strong>{currency(budget.limit)}</strong>
              <button className="icon-button danger" onClick={() => deleteBudget(budget.id)} aria-label="Delete budget"><Trash2 size={16} /></button>
            </div>
          ))}
          {!budgets.length && <p className="muted">No budgets yet.</p>}
        </div>
      </section>
    </div>
  );
}
