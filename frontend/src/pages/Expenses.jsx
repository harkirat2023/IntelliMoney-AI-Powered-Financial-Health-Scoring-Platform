import { useEffect, useState } from "react";
import { Sparkles, Trash2 } from "lucide-react";

import { api } from "../api/client";
import { currency, today } from "../utils/format";

const categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Travel", "Rent", "Other"];
const paymentMethods = ["Cash", "Card", "UPI", "Bank Transfer", "Wallet", "Other"];

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
      await api.post("/expenses", {
        ...form,
        amount: Number(form.amount),
        category: form.category || null
      });
      setForm(initialForm);
      setPrediction(null);
      await loadExpenses();
    } catch {
      setError("Could not save expense.");
    }
  }

  async function deleteExpense(id) {
    await api.delete(`/expenses/${id}`);
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
          <h2>Add Expense</h2>
          <label>Amount<input type="number" min="1" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></label>
          <label>Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="e.g. Uber ride to office" required /></label>
          <button className="secondary" type="button" onClick={predictCategory}><Sparkles size={16} /> Predict Category</button>
          {prediction && <div className="prediction">Predicted {prediction.category} with {Math.round(prediction.confidence * 100)}% confidence</div>}
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              <option value="">Auto categorize</option>
              {categories.map((category) => <option key={category}>{category}</option>)}
            </select>
          </label>
          <label>Payment method
            <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
              {paymentMethods.map((method) => <option key={method}>{method}</option>)}
            </select>
          </label>
          <label>Date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">Save Expense</button>
        </form>

        <article className="panel list-panel">
          <div className="panel-title-row">
            <h2>Transactions</h2>
            <div className="filters">
              <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
                <option value="">All categories</option>
                {categories.map((category) => <option key={category}>{category}</option>)}
              </select>
              <select value={filters.payment_method} onChange={(e) => setFilters({ ...filters, payment_method: e.target.value })}>
                <option value="">All methods</option>
                {paymentMethods.map((method) => <option key={method}>{method}</option>)}
              </select>
            </div>
          </div>
          <div className="table">
            {expenses.map((expense) => (
              <div className="table-row" key={expense.id}>
                <span>{expense.description}<small>{expense.date}</small></span>
                <span>{expense.category}</span>
                <strong>{currency(expense.amount)}</strong>
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
