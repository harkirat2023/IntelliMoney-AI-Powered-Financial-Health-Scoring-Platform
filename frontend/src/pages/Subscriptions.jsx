import { useEffect, useState } from "react";
import { Plus, RefreshCw, Trash2, X, DollarSign, TrendingUp, Lightbulb } from "lucide-react";

import { api } from "../api/client";
import { FREQUENCIES, SUBSCRIPTION_CATEGORIES } from "../config/constants";
import { currency } from "../utils/format";

const initialForm = {
  description: "",
  amount: "",
  category: "Entertainment",
  frequency: "monthly",
  start_date: new Date().toISOString().split('T')[0],
  end_date: "",
  is_active: true,
};

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [insights, setInsights] = useState(null);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showInsights, setShowInsights] = useState(true);

  async function loadData() {
    try {
      const [subsRes, suggestionsRes, insightsRes] = await Promise.all([
        api.get("/subscriptions"),
        api.get("/subscriptions/suggestions/detect"),
        api.get("/subscriptions/insights"),
      ]);
      setSubscriptions(subsRes.data);
      setSuggestions(suggestionsRes.data);
      setInsights(insightsRes.data);
    } catch {
      setError("Could not load subscriptions.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function saveSubscription(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        ...form,
        amount: Number(form.amount),
        end_date: form.end_date || null,
      };
      if (editingId) {
        await api.put(`/subscriptions/${editingId}`, payload);
      } else {
        await api.post("/subscriptions", payload);
      }
      setForm(initialForm);
      setEditingId(null);
      await loadData();
    } catch {
      setError("Could not save subscription.");
    }
  }

  function editSubscription(sub) {
    setEditingId(sub.id);
    setForm({
      description: sub.description,
      amount: sub.amount,
      category: sub.category,
      frequency: sub.frequency,
      start_date: sub.start_date,
      end_date: sub.end_date || "",
      is_active: sub.is_active,
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(initialForm);
  }

  async function deleteSubscription(id) {
    await api.delete(`/subscriptions/${id}`);
    if (editingId === id) cancelEdit();
    await loadData();
  }

  async function addSuggestion(suggestion) {
    setForm({
      description: suggestion.description,
      amount: suggestion.amount,
      category: suggestion.category,
      frequency: suggestion.frequency,
      start_date: suggestion.suggested_start_date,
      end_date: "",
      is_active: true,
    });
    setEditingId(null);
    setShowSuggestions(false);
  }

  async function recordPayment(id) {
    try {
      await api.post(`/subscriptions/${id}/record-payment`);
      await loadData();
    } catch {
      setError("Could not record payment.");
    }
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

  function getMonthlyCost(amount, frequency) {
    if (frequency === "weekly") return amount * 4.33;
    if (frequency === "biweekly") return amount * 2.17;
    if (frequency === "monthly") return amount;
    if (frequency === "yearly") return amount / 12;
    return amount;
  }

  if (loading) return <div className="centered">Loading subscriptions...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Subscription Tracker</h1>
          <p>Track and manage your recurring subscriptions</p>
        </div>
        <div className="header-actions">
          <button className="secondary" onClick={() => setShowInsights(!showInsights)}>
            <Lightbulb size={16} />
            {showInsights ? "Hide" : "Show"} Insights
          </button>
          <button className="secondary" onClick={() => setShowSuggestions(!showSuggestions)}>
            <RefreshCw size={16} />
            {showSuggestions ? "Hide" : "Show"} Suggestions
          </button>
        </div>
      </header>

      {showInsights && insights && (
        <section className="panel insights-panel">
          <h2>📊 Subscription Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <DollarSign size={24} />
              <div>
                <span className="insight-label">Monthly Cost</span>
                <span className="insight-value">{currency(insights.total_monthly_cost)}</span>
              </div>
            </div>
            <div className="insight-card">
              <TrendingUp size={24} />
              <div>
                <span className="insight-label">Yearly Cost</span>
                <span className="insight-value">{currency(insights.total_yearly_cost)}</span>
              </div>
            </div>
            <div className="insight-card">
              <div>
                <span className="insight-label">Active Subscriptions</span>
                <span className="insight-value">{insights.active_subscriptions}</span>
              </div>
            </div>
          </div>
          <div className="insights-list">
            {insights.insights.map((insight, index) => (
              <div key={index} className="insight-item">
                {insight}
              </div>
            ))}
          </div>
        </section>
      )}

      {showSuggestions && suggestions.length > 0 && (
        <section className="panel suggestions-panel">
          <h2>🤖 Detected Subscriptions</h2>
          <p className="muted">We found these potential subscriptions from your expenses:</p>
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
                  <span>{getFrequencyLabel(suggestion.frequency)}</span>
                  <span>{suggestion.occurrences_detected} payments</span>
                  <span>Total: {currency(suggestion.total_spent)}</span>
                </div>
                <button className="primary" onClick={() => addSuggestion(suggestion)}>
                  <Plus size={16} />
                  Add as Subscription
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="split">
        <form className="panel form-panel" onSubmit={saveSubscription}>
          <div className="panel-title-row">
            <h2>{editingId ? "Edit Subscription" : "Add Subscription"}</h2>
            {editingId && (
              <button className="icon-button" type="button" onClick={cancelEdit} aria-label="Cancel edit">
                <X size={16} />
              </button>
            )}
          </div>
          <label>Description<input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="e.g. Netflix, Spotify" required /></label>
          <label>Amount<input type="number" min="1" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></label>
          <label>Category
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {SUBSCRIPTION_CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
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
          <button type="submit">{editingId ? "Update" : "Add Subscription"}</button>
        </form>

        <article className="panel list-panel">
          <h2>Your Subscriptions ({subscriptions.length})</h2>
          {subscriptions.length === 0 ? (
            <div className="empty-state">
              <RefreshCw size={48} />
              <p>No subscriptions yet. Add one or use smart suggestions!</p>
            </div>
          ) : (
            <div className="subscriptions-list">
              {subscriptions.map((sub) => (
                <div key={sub.id} className={`subscription-card ${!sub.is_active ? "inactive" : ""}`}>
                  <div className="subscription-header">
                    <div className="subscription-info">
                      <strong>{sub.description}</strong>
                      <span className="subscription-meta">
                        {sub.category} · {getFrequencyLabel(sub.frequency)}
                      </span>
                    </div>
                    <div className="subscription-actions">
                      <button
                        className="secondary"
                        onClick={() => recordPayment(sub.id)}
                        title="Record Payment"
                      >
                        <DollarSign size={16} />
                      </button>
                      <button className="icon-button" onClick={() => editSubscription(sub)} aria-label="Edit">
                        <RefreshCw size={16} />
                      </button>
                      <button className="icon-button danger" onClick={() => deleteSubscription(sub.id)} aria-label="Delete">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="subscription-body">
                    <div className="subscription-stats">
                      <div className="stat">
                        <span className="stat-label">Amount</span>
                        <span className="stat-value">{currency(sub.amount)}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Monthly Cost</span>
                        <span className="stat-value">{currency(getMonthlyCost(sub.amount, sub.frequency))}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Total Spent</span>
                        <span className="stat-value">{currency(sub.total_spent)}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Payments</span>
                        <span className="stat-value">{sub.payment_count}</span>
                      </div>
                    </div>
                    {sub.next_payment_date && (
                      <div className="next-payment">
                        <span>Next payment: {new Date(sub.next_payment_date).toLocaleDateString()}</span>
                      </div>
                    )}
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