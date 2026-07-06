import { useEffect, useState } from "react";
import { Pencil, Sparkles, Trash2, X } from "lucide-react";

import { api } from "../api/client";
import { CATEGORIES, PAYMENT_METHODS } from "../config/constants";
import { currency, today } from "../utils/format";

const initialForm = {
  amount: "",
  description: "",
  category: "",
  payment_method: "UPI",
  date: today()
};

export default function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [filters, setFilters] = useState({ category: "", payment_method: "" });
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState("");

  async function loadExpenses() {
    const params = Object.fromEntries(Object.entries(filters).filter(([, value]) => value));
    const response = await api.get("/expenses", { params });
    setExpenses(response.data);
  }

  useEffect(() => {
    loadExpenses().catch(() => setError("Could not load expenses."));
  }, [filters]);

  async function predictCategory() {
    if (!form.description.trim()) return;
    const response = await api.post("/ml/categorize", { description: form.description });
    setPrediction(response.data);
    setForm((current) => ({ ...current, category: response.data.category }));
  }

  async function saveExpense(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        amount: Number(form.amount),
        category: form.category || null
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
      setError("Could not save expense.");
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
      date: expense.date
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

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Expenses</h1>
          <p>Add expenses and let the NLP model suggest categories.</p>
        </div>
      </header>

      <section className="split">
        <form className="panel form-panel" onSubmit={saveExpense}>
          <div className="panel-title-row">
            <h2>{editingId ? "Edit Expense" : "Add Expense"}</h2>
            {editingId && <button className="icon-button" type="button" onClick={cancelEdit} aria-label="Cancel edit"><X size={16} /></button>}
          </div>
          <label>Amount<input type="number" min="1" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></label>
          <label>Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="e.g. Uber ride to office" required /></label>
          <button className="secondary" type="button" onClick={predictCategory}><Sparkles size={16} /> Predict Category</button>
          {prediction && <div className="prediction">Predicted {prediction.category} with {Math.round(prediction.confidence * 100)}% confidence</div>}
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              <option value="">Auto categorize</option>
              {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
            </select>
          </label>
          <label>Payment method
            <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
              {PAYMENT_METHODS.map((method) => <option key={method}>{method}</option>)}
            </select>
          </label>
          <label>Date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">{editingId ? "Update Expense" : "Save Expense"}</button>
        </form>

        <article className="panel list-panel">
          <div className="panel-title-row">
            <h2>Transactions</h2>
            <div className="filters">
              <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
                <option value="">All categories</option>
                {CATEGORIES.map((category) => <option key={category}>{category}</option>)}
              </select>
              <select value={filters.payment_method} onChange={(e) => setFilters({ ...filters, payment_method: e.target.value })}>
                <option value="">All methods</option>
                {PAYMENT_METHODS.map((method) => <option key={method}>{method}</option>)}
              </select>
            </div>
          </div>
          <div className="table">
            {expenses.map((expense) => (
              <div className="table-row" key={expense.id}>
                <span>{expense.description}<small>{expense.date}</small></span>
                <span>{expense.category}</span>
                <strong>{currency(expense.amount)}</strong>
                <button className="icon-button" onClick={() => editExpense(expense)} aria-label="Edit expense"><Pencil size={16} /></button>
                <button className="icon-button danger" onClick={() => deleteExpense(expense.id)} aria-label="Delete expense"><Trash2 size={16} /></button>
              </div>
            ))}
            {!expenses.length && <p className="muted">No matching expenses.</p>}
          </div>
        </article>
      </section>
    </div>
  );
}
