import { useCallback, useEffect, useState } from "react";
import { Pencil, Plus, Trash2, X } from "lucide-react";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import { dashboardV2Api } from "../../api/dashboardV2";
import { api } from "../../api/client";
import { CATEGORIES } from "../../config/constants";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

const initialForm = { category: "", limit: "" };

export default function BudgetsPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [budgets, setBudgets] = useState(null);
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const loadBudgets = useCallback(async () => {
    try {
      const res = await dashboardV2Api.getBudgets(period);
      setBudgets(res.data);
      setError("");
    } catch {
      setError("Could not load budgets.");
    }
  }, [period]);

  useEffect(() => {
    loadBudgets();
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, [loadBudgets]);

  const parsePeriod = () => {
    const [y, m] = period.split("-").map(Number);
    return { year: y, month: m };
  };

  async function saveBudget(event) {
    event.preventDefault();
    setError("");
    const { year, month } = parsePeriod();
    const payload = { category: form.category, limit: Number(form.limit), month, year };
    try {
      if (editingId) {
        await api.put(`/budgets/${editingId}`, { limit: payload.limit });
      } else {
        await api.post("/budgets", payload);
      }
      setForm(initialForm);
      setEditingId(null);
      await loadBudgets();
    } catch {
      setError("Could not save budget.");
    }
  }

  function editBudget(budget) {
    setEditingId(budget.id);
    setError("");
    setForm({ category: budget.category, limit: budget.limit });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(initialForm);
  }

  async function deleteBudget(id) {
    await api.delete(`/budgets/${id}`);
    if (editingId === id) cancelEdit();
    await loadBudgets();
  }

  if (!budgets) return <DashboardSkeleton />;

  const totalLimit = budgets.budgets?.reduce((sum, b) => sum + (b.limit || 0), 0) || 0;
  const totalSpent = budgets.budgets?.reduce((sum, b) => sum + (b.spent || 0), 0) || 0;

  return (
    <div className="dash-page">
      <div className="im-page-header">
        <div>
          <h1 className="im-page-title">Budgets</h1>
          <p className="im-page-subtitle">Budget performance for {period}.</p>
        </div>
        <input type="month" className="im-field dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="im-grid im-grid-4">
        <div className="im-card stat-widget">
          <span className="widget-label">Total Budget</span>
          <div className="im-metric-value">{currency(totalLimit)}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">Total Spent</span>
          <div className="im-metric-value">{currency(totalSpent)}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">On Track</span>
          <div className="im-metric-value" style={{ color: "var(--ds-ok-strong)" }}>{budgets.on_track}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">Over Budget</span>
          <div className="im-metric-value" style={{ color: "var(--ds-danger-strong)" }}>{budgets.over}</div>
        </div>
      </div>

      <div className="im-card">
        <h3 className="im-h3" style={{ margin: "0 0 16px" }}>{editingId ? "Edit Budget" : "Add Budget"}</h3>
        <form className="budget-form im-inline-form" onSubmit={saveBudget}>
          <select className="im-field" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required disabled={!!editingId}>
            <option value="">Select category</option>
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
          <input className="im-field" type="number" min="1" step="0.01" placeholder="Monthly limit (₹)" value={form.limit}
            onChange={(e) => setForm({ ...form, limit: e.target.value })} required />
          {editingId && (
            <button className="im-btn im-btn-ghost" type="button" onClick={cancelEdit}><X size={14} /> Cancel</button>
          )}
          <button className="im-btn im-btn-primary" type="submit">{editingId ? "Update" : <><Plus size={14} /> Add Budget</>}</button>
        </form>
        {error && <p className="expense-error">{error}</p>}
      </div>

      <div className="im-grid im-grid-3">
        {budgets.budgets?.map((b) => {
          const pct = b.percentage_used || 0;
          const over = b.state === "over";
          const danger = b.state === "warning" || b.state === "critical";
          const badgeClass = over ? "danger" : danger ? "warning" : "ok";
          const fillColor = over ? "var(--ds-danger)" : b.state === "critical" ? "var(--ds-warning-strong, #f97316)" : danger ? "var(--ds-warning)" : "var(--ds-primary)";
          return (
            <div className="im-card im-budget-card" key={b.id}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <strong style={{ fontSize: "0.95rem", color: "var(--neutral-800)" }}>{b.category}</strong>
                <span className={`im-badge ${badgeClass}`}>{b.state}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
                <strong style={{ fontSize: "1.25rem", color: "var(--neutral-900)" }}>{currency(b.spent)}</strong>
                <span style={{ color: "var(--neutral-500)", fontSize: "0.82rem" }}>/ {currency(b.limit)}</span>
              </div>
              <div className="im-progress">
                <div className="im-progress-fill" style={{ width: `${Math.min(pct, 100)}%`, background: fillColor }} />
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 10 }}>
                <span style={{ fontSize: "0.82rem", color: "var(--neutral-500)" }}>
                  {pct.toFixed(1)}% used · {over ? `Over by ${currency(b.spent - b.limit)}` : `${currency(b.limit - b.spent)} remaining`}
                </span>
                <div style={{ display: "flex", gap: 6 }}>
                  <button className="im-icon-btn" onClick={() => editBudget(b)} aria-label="Edit budget"><Pencil size={14} /></button>
                  <button className="im-icon-btn danger" onClick={() => deleteBudget(b.id)} aria-label="Delete budget"><Trash2 size={14} /></button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {budgets.budgets?.length === 0 && (
        <div className="im-empty">
          <h3>No budgets yet</h3>
          <p>Create a budget above to start tracking your spending.</p>
        </div>
      )}
    </div>
  );
}