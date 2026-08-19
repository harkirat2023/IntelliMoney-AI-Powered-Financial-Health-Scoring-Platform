import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
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

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Budgets</h1>
          <p className="dash-subtitle">Budget performance for {period}</p>
        </div>
        <input type="month" className="dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="budget-summary-strip">
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.on_track}</span><span className="budget-summary-label safe">On Track</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.warning}</span><span className="budget-summary-label warning">Warning</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.over}</span><span className="budget-summary-label over">Over</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.budgets?.length || 0}</span><span className="budget-summary-label">Total</span></div>
      </div>

      <div className="dash-panel">
        <h3 className="dash-panel-title">{editingId ? "Edit Budget" : "Add Budget"}</h3>
        <form className="budget-form" onSubmit={saveBudget}>
          <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} required disabled={!!editingId}>
            <option value="">Select category</option>
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
          <input type="number" min="1" step="0.01" placeholder="Monthly limit (₹)" value={form.limit}
            onChange={(e) => setForm({ ...form, limit: e.target.value })} required />
          {editingId && (
            <button className="btn-ghost" type="button" onClick={cancelEdit}><X size={14} /> Cancel</button>
          )}
          <button className="btn-primary" type="submit">{editingId ? "Update" : <><Plus size={14} /> Add Budget</>}</button>
        </form>
        {error && <p className="expense-error">{error}</p>}
      </div>

      <div className="dash-budget-grid">
        {budgets.budgets?.map((b, i) => {
          const pct = b.percentage_used || 0;
          return (
            <div className={`dash-budget-card ${b.state}`} key={i}>
              <div className="budget-card-header">
                <strong>{b.category}</strong>
                <span className={`budget-state-badge ${b.state}`}>{b.state}</span>
              </div>
              <div className="budget-card-amounts">
                <span>{currency(b.spent)}</span>
                <span className="budget-limit">/ {currency(b.limit)}</span>
              </div>
              <div className="budget-progress-bar">
                <div className="budget-progress-fill" style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
              <div className="budget-pct">{pct.toFixed(1)}% used</div>
              <div className="budget-remaining">
                {b.state === "over"
                  ? `Over by ${currency(b.spent - b.limit)}`
                  : `${currency(b.limit - b.spent)} remaining`}
              </div>
              <div className="budget-card-actions">
                <button className="icon-button" onClick={() => editBudget(b)} aria-label="Edit budget"><Pencil size={14} /></button>
                <button className="icon-button danger" onClick={() => deleteBudget(b.id)} aria-label="Delete budget"><Trash2 size={14} /></button>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
