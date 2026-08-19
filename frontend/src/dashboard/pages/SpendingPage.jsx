import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Pencil, Sparkles, Trash2, X } from "lucide-react";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import PieChartCard from "../charts/PieChartCard";
import AreaChartCard from "../charts/AreaChartCard";
import BarChartCard from "../charts/BarChartCard";
import { api } from "../../api/client";
import { CATEGORIES, PAYMENT_METHODS } from "../../config/constants";
import { currency, today } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

const initialForm = { amount: "", description: "", category: "", payment_method: "UPI", date: today() };

export default function SpendingPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [formError, setFormError] = useState("");

  const loadExpenses = useCallback(async () => {
    const [year, month] = period.split("-");
    try {
      const res = await api.get("/expenses", { params: { start_date: `${period}-01`, end_date: `${period}-31` } });
      setExpenses(res.data);
      await dashboardV2Store.fetchOverview(period);
      await dashboardV2Store.fetchWidgets(["spending_heatmap", "top_categories"], period);
    } catch {
      // Overview fetch already surfaces loading errors.
    }
  }, [period]);

  useEffect(() => {
    dashboardV2Store.fetchOverview(period);
    dashboardV2Store.fetchWidgets(["spending_heatmap", "top_categories"], period);
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, [period]);

  useEffect(() => {
    loadExpenses().catch(() => setFormError("Could not load expenses."));
  }, [loadExpenses]);

  async function predictCategory() {
    if (!form.description.trim()) return;
    try {
      const res = await api.post("/expenses/categorize", { description: form.description });
      setPrediction(res.data);
      setForm((current) => ({ ...current, category: res.data.category }));
    } catch {
      setFormError("Could not suggest a category.");
    }
  }

  async function saveExpense(event) {
    event.preventDefault();
    setFormError("");
    try {
      const payload = {
        amount: Number(form.amount),
        description: form.description,
        category: form.category || null,
        payment_method: form.payment_method,
        date: form.date,
      };
      if (editingId) {
        await api.put(`/expenses/${editingId}`, payload);
      } else {
        await api.post("/expenses", payload);
      }
      setForm(initialForm);
      setEditingId(null);
      setPrediction(null);
      await loadExpenses();
    } catch {
      setFormError("Could not save expense.");
    }
  }

  function editExpense(expense) {
    setEditingId(expense.id);
    setPrediction(null);
    setForm({
      amount: expense.amount,
      description: expense.description,
      category: expense.category,
      payment_method: expense.payment_method,
      date: expense.date,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setPrediction(null);
    setForm(initialForm);
  }

  async function deleteExpense(id) {
    await api.delete(`/expenses/${id}`);
    if (editingId === id) cancelEdit();
    await loadExpenses();
  }

  const { overview, widgets, loading } = state;
  const spending = overview?.spending;

  if (loading && !spending) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Spending</h1>
          <p className="dash-subtitle">Detailed spending analysis and transaction management</p>
        </div>
        <input type="month" className="dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="dash-stats-grid">
        <div className="dash-widget stat-widget">
          <div className="widget-label">Total Spending</div>
          <div className="dash-stat-value">{currency(spending?.total_spending || 0)}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Transactions</div>
          <div className="dash-stat-value">{spending?.expense_count || 0}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Top Category</div>
          <div className="dash-stat-value">{spending?.top_category || "N/A"}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Avg per Transaction</div>
          <div className="dash-stat-value">
            {spending?.expense_count ? currency(spending.total_spending / spending.expense_count) : currency(0)}
          </div>
        </div>
      </div>

      <div className="dash-overview-grid">
        {spending?.spending_by_category?.length > 0 && (
          <PieChartCard title="By Category" data={spending.spending_by_category} height={320} />
        )}
        {overview?.monthly_trend?.length > 0 && (
          <AreaChartCard title="Monthly Trend" data={overview.monthly_trend} dataKey="spending" height={320} />
        )}
        {overview?.top_categories?.length > 0 && (
          <BarChartCard title="Top Categories" data={overview.top_categories} dataKey="amount" height={320} />
        )}
      </div>

      {widgets.spending_heatmap?.length > 0 && (
        <div className="dash-panel">
          <h3 className="dash-panel-title">Spending Activity</h3>
          <div className="heatmap-grid">
            {widgets.spending_heatmap.map((h, i) => (
              <div className="heatmap-cell" key={i} title={`${h.category}: ${currency(h.amount)}`}>
                <div className="heatmap-bar" style={{ height: `${Math.min((h.amount / 10000) * 100, 100)}%` }} />
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="dash-panel expense-manager">
        <h3 className="dash-panel-title">{editingId ? "Edit Expense" : "Add Expense"}</h3>
        <form className="expense-form" onSubmit={saveExpense}>
          <input type="number" min="1" step="0.01" placeholder="Amount (₹)" value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
          <input placeholder="Description (e.g. Uber ride to office)" value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })} required />
          <button className="btn-secondary" type="button" onClick={predictCategory}>
            <Sparkles size={14} /> Suggest
          </button>
          <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
            <option value="">Auto categorize</option>
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
          <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
            {PAYMENT_METHODS.map((m) => <option key={m}>{m}</option>)}
          </select>
          <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required />
          {editingId && (
            <button className="btn-ghost" type="button" onClick={cancelEdit}><X size={14} /> Cancel</button>
          )}
          <button className="btn-primary" type="submit">{editingId ? "Update" : "Add"}</button>
        </form>
        {prediction && <p className="expense-prediction">Suggested: {prediction.category} ({Math.round(prediction.confidence * 100)}%)</p>}
        {formError && <p className="expense-error">{formError}</p>}
      </div>

      <div className="dash-panel">
        <h3 className="dash-panel-title">Transactions</h3>
        <div className="expense-table">
          {expenses.length === 0 && <p className="dash-subtitle">No expenses for this period.</p>}
          {expenses.map((expense) => (
            <div className="expense-row" key={expense.id}>
              <div className="expense-info">
                <strong>{expense.description}</strong>
                <small>{expense.date} · {expense.payment_method}</small>
              </div>
              <span className="expense-category">{expense.category}</span>
              <strong>{currency(expense.amount)}</strong>
              <div className="expense-actions">
                <button className="icon-button" onClick={() => editExpense(expense)} aria-label="Edit expense"><Pencil size={14} /></button>
                <button className="icon-button danger" onClick={() => deleteExpense(expense.id)} aria-label="Delete expense"><Trash2 size={14} /></button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}