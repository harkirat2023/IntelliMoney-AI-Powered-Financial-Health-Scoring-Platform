import { useEffect, useState } from "react";
import { Check, RefreshCw, TrendingDown, TrendingUp, X } from "lucide-react";

import { api } from "../api/client";
import { currency } from "../utils/format";

export default function BudgetOptimizer() {
  const [suggestions, setSuggestions] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [applyingId, setApplyingId] = useState(null);
  const [dismissingId, setDismissingId] = useState(null);

  async function loadData() {
    try {
      const [suggestionsRes, reportRes] = await Promise.all([
        api.get("/budget-suggestions"),
        api.get("/budget-suggestions/optimization-report"),
      ]);
      setSuggestions(suggestionsRes.data);
      setReport(reportRes.data);
    } catch {
      setError("Could not load budget suggestions.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function generateSuggestions() {
    try {
      await api.post("/budget-suggestions/generate");
      await loadData();
    } catch {
      setError("Could not generate suggestions.");
    }
  }

  async function applySuggestion(id) {
    setApplyingId(id);
    try {
      await api.post(`/budget-suggestions/${id}/apply`);
      await loadData();
    } catch {
      setError("Could not apply suggestion.");
    } finally {
      setApplyingId(null);
    }
  }

  async function dismissSuggestion(id) {
    setDismissingId(id);
    try {
      await api.delete(`/budget-suggestions/${id}`);
      await loadData();
    } catch {
      setError("Could not dismiss suggestion.");
    } finally {
      setDismissingId(null);
    }
  }

  function getChangeColor(change) {
    if (change > 0) return "#dc2626"; // Red for increase
    if (change < 0) return "#16a34a"; // Green for decrease
    return "#65738b";
  }

  function getChangeIcon(change) {
    if (change > 0) return <TrendingUp size={16} />;
    if (change < 0) return <TrendingDown size={16} />;
    return null;
  }

  if (loading) return <div className="centered">Loading budget optimizer...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Smart Budget Optimizer</h1>
          <p>AI-powered suggestions to optimize your budget allocations</p>
        </div>
        <button className="secondary" onClick={generateSuggestions}>
          <RefreshCw size={16} />
          Generate Suggestions
        </button>
      </header>

      {report && (
        <section className="panel report-panel">
          <h2>Optimization Report</h2>
          <div className="report-overview">
            <div className="report-card">
              <span className="report-label">Total Budget</span>
              <span className="report-value">{currency(report.total_budget)}</span>
            </div>
            <div className="report-card">
              <span className="report-label">Suggested Total</span>
              <span className="report-value">{currency(report.total_suggested)}</span>
            </div>
            <div className={`report-card ${report.potential_savings > 0 ? "savings" : "increase"}`}>
              <span className="report-label">
                {report.potential_savings > 0 ? "Potential Savings" : "Needed Increase"}
              </span>
              <span className="report-value">
                {currency(Math.abs(report.potential_savings))}
              </span>
            </div>
          </div>

          <div className="insights">
            <h3>Insights</h3>
            <div className="insights-list">
              {report.insights.map((insight, index) => (
                <div key={index} className="insight-item">
                  {insight}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="panel">
        <h2>Budget Suggestions ({suggestions.length})</h2>
        {suggestions.length === 0 ? (
          <div className="empty-state">
            <RefreshCw size={48} />
            <p>No suggestions yet. Click "Generate Suggestions" to analyze your spending patterns.</p>
          </div>
        ) : (
          <div className="suggestions-list">
            {suggestions.map((suggestion) => (
              <div key={suggestion.id} className="suggestion-card">
                <div className="suggestion-header">
                  <div className="suggestion-title">
                    <strong>{suggestion.category}</strong>
                    <span className="confidence-badge">
                      {Math.round(suggestion.confidence * 100)}% confidence
                    </span>
                  </div>
                  <div className="suggestion-actions">
                    <button
                      className="secondary"
                      onClick={() => dismissSuggestion(suggestion.id)}
                      disabled={dismissingId === suggestion.id}
                    >
                      <X size={16} />
                    </button>
                    <button
                      className="primary"
                      onClick={() => applySuggestion(suggestion.id)}
                      disabled={applyingId === suggestion.id}
                    >
                      <Check size={16} />
                      {applyingId === suggestion.id ? "Applying..." : "Apply"}
                    </button>
                  </div>
                </div>

                <div className="suggestion-body">
                  <div className="budget-comparison">
                    <div className="budget-item">
                      <span className="budget-label">Current Limit</span>
                      <span className="budget-value">{currency(suggestion.current_limit)}</span>
                    </div>
                    <div className="budget-arrow">
                      {getChangeIcon(suggestion.change)}
                    </div>
                    <div className="budget-item">
                      <span className="budget-label">Suggested Limit</span>
                      <span className="budget-value" style={{ color: getChangeColor(suggestion.change) }}>
                        {currency(suggestion.suggested_limit)}
                      </span>
                    </div>
                  </div>

                  <div className="change-indicator" style={{ color: getChangeColor(suggestion.change) }}>
                    {suggestion.change > 0 ? "+" : ""}
                    {currency(suggestion.change)} ({suggestion.change_percentage}%)
                  </div>

                  <div className="suggestion-stats">
                    <div className="stat">
                      <span className="stat-label">Average Spending</span>
                      <span className="stat-value">{currency(suggestion.average_spending)}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Max Spending</span>
                      <span className="stat-value">{currency(suggestion.max_spending)}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Min Spending</span>
                      <span className="stat-value">{currency(suggestion.min_spending)}</span>
                    </div>
                  </div>

                  <p className="suggestion-reason">{suggestion.reason}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}