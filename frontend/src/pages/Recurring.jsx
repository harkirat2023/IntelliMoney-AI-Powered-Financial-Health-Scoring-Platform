import { useEffect, useState } from "react";
import { Plus, Sparkles, Trash2, X, Calendar, RefreshCw } from "lucide-react";

import { api } from "../api/client";
import { CATEGORIES, FREQUENCIES } from "../config/constants";
import { currency } from "../utils/format";

const initialForm = {
  description: "",
  amount: "",
  category: "Bills",
  frequency: "monthly",
  start_date: new Date().toISOString().split('T')[0],
  end_date: "",
  is_active: true,
};

export default function Recurring() {
  const [recurring, setRecurring] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [upcoming, setUpcoming] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showUpcoming, setShowUpcoming] = useState(false);

  async function loadRecurring() {
    try {
      const [recurringRes, suggestionsRes, upcomingRes] = await Promise.all([
        api.get("/recurring"),
        api.get("/recurring/suggestions/detect"),
        api.get("/recurring/upcoming?days_ahead=30"),
      ]);
      setRecurring(recurringRes.data);
      setSuggestions(suggestionsRes.data);
      setUpcoming(upcomingRes.data);
    } catch {
      setError("Could not load recurring expenses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRecurring();
  }, []);

  async function saveRecurring(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        amount: Number(form.amount),
        end_date: form.end_date || null,
      };
      if (editingId) {
        await api.put(`/recurring/${editingId}`, payload);
      } else {
        await api.post("/recurring", payload);
      }
      setForm(initialForm);
      setEditingId(null);
      await loadRecurring();
    } catch {
      setError("Could not save recurring expense.");
    }
  }

  function editRecurring(item) {
    setEditingId(item.id);
    setForm({
      description: item.description,
      amount: item.amount,
      category: item.category,
      frequency: item.frequency,
      start_date: item.start_date,
      end_date: item.end_date || "",
      is_active: item.is_active,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(initialForm);
  }

  async function deleteRecurring(id) {
    await api.delete(`/recurring/${id}`);
    if (editingId === id) cancelEdit();
    await loadRecurring();
  }

  async function addSuggestion(suggestion) {
    setForm({
      description: suggestion.description,
      amount: suggestion.amount,
      category: suggestion.category,
      frequency: suggestion.frequency,
      start_date: suggestion.suggested_start_date,
      end_date: suggestion.suggested_end_date || "",
      is_active: true,
    });
    setEditingId(null);
    setShowSuggestions(false);
  }

  function getFrequencyLabel(frequency) {
    const labels = {
      weekly: "Weekly",
      biweekly: "Bi-weekly",
      monthly: "Monthly",
      yearly: "Yearly",
    };
    return labels[frequency] || frequency;
  }

  if (loading) return <div className="centered">Loading recurring expenses...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Recurring Expenses</h1>
          <p>Automatically track subscriptions, bills, and regular payments.</p>
        </div>
        <div className="header-actions">
          <button className="secondary" onClick={() => setShowSuggestions(!showSuggestions)}>
            <Sparkles size={16} />
            {showSuggestions ? "Hide" : "Show"} Suggestions
          </button>
          <button className="secondary" onClick={() => setShowUpcoming(!showUpcoming)}>
            <Calendar size={16} />
            {showUpcoming ? "Hide" : "Show"} Upcoming
          </button>
        </div>
      </header>

      {showSuggestions && suggestions.length > 0 && (
        <section className="panel suggestions-panel">
          <h2>🤖 Smart Suggestions</h2>
          <p className="muted">We detected these recurring patterns from your expenses:</p>
          <div className="suggestions-grid">
            {suggestions.map((suggestion, index) => (
              <div className="suggestion-card" key={index}>
                <div className="suggestion-header">
                  <strong>{suggestion.description}</strong>
                  <span className="confidence-badge">
                    {Math.round(suggestion.confidence * 100)}% match
                  </span>
                </div>
                <div className="suggestion-details">
                  <span>{currency(suggestion.amount)}</span>
                  <span>{suggestion.category}</span>
                  <span>{getFrequencyLabel(suggestion.frequency)}</span>
                  <span>{suggestion.occurrences_detected} occurrences</span>
                </div>
                <button className="primary" onClick={() => addSuggestion(suggestion)}>
                  <Plus size={16} />
                  Add as Recurring
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {showUpcoming && upcoming.length > 0 && (
        <section className="panel upcoming-panel">
          <h2>📅 Upcoming Expenses (Next 30 Days)</h2>
          <div className="upcoming-list">
            {upcoming.map((item, index) => (
              <div className="upcoming-item" key={index}>
                <div className="upcoming-info">
                  <strong>{item.description}</strong>
                  <span>{item.category}</span>
                </div>
                <div className="upcoming-meta">
                  <span className="upcoming-date">{item.expected_date}</span>
                  <span className="upcoming-amount">{currency(item.amount)}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="split">
        <form className="panel form-panel" onSubmit={saveRecurring}>
          <div className="panel-title-row">
            <h2>{editingId ? "Edit Recurring Expense" : "Add Recurring Expense"}</h2>
            {editingId && (
              <button className="icon-button" type="button" onClick={cancelEdit} aria-label="Cancel edit">
                <X size={16} />
              </button>
            )}
          </div>
          <label>Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="e.g. Netflix Subscription" required /></label>
          <label>Amount<input type="number" min="1" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></label>
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
            </select>
          </label>
          <label>Frequency
            <select value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}>
              {FREQUENCIES.map((freq) => <option key={freq} value={freq}>{getFrequencyLabel(freq)}</option>)}
            </select>
          </label>
          <label>Start Date<input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} required /></label>
          <label>End Date (Optional)<input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} /></label>
          {error && <div className="error">{error}</div>}
          <button type="submit">{editingId ? "Update" : "Add Recurring Expense"}</button>
        </form>

        <article className="panel list-panel">
          <h2>Your Recurring Expenses</h2>
          {recurring.length === 0 ? (
            <p className="muted">No recurring expenses yet. Add one or use smart suggestions!</p>
          ) : (
            <div className="table">
              {recurring.map((item) => (
                <div className="table-row" key={item.id}>
                  <div className="recurring-info">
                    <span className="recurring-description">{item.description}</span>
                    <span className="recurring-meta">
                      {item.category} · {getFrequencyLabel(item.frequency)}
                    </span>
                  </div>
                  <strong>{currency(item.amount)}</strong>
                  <div className="recurring-actions">
                    <button className="icon-button" onClick={() => editRecurring(item)} aria-label="Edit">
                      <RefreshCw size={16} />
                    </button>
                    <button className="icon-button danger" onClick={() => deleteRecurring(item.id)} aria-label="Delete">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </div>
  );
}