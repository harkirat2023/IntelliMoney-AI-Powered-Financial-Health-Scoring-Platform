import { useEffect, useState } from "react";
import { FileText, RefreshCw, TrendingUp, DollarSign, Target } from "lucide-react";

import { api } from "../api/client";
import { currency } from "../utils/format";

export default function Reports() {
  const [reports, setReports] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedReport, setSelectedReport] = useState(null);
  const [filter, setFilter] = useState("all"); // all, weekly, monthly

  async function loadData() {
    try {
      const [reportsRes, summaryRes] = await Promise.all([
        api.get(`/reports?report_type=${filter === "all" ? "" : filter}`),
        api.get("/reports/summary"),
      ]);
      setReports(reportsRes.data);
      setSummary(summaryRes.data);
    } catch {
      setError("Could not load reports.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [filter]);

  async function generateWeekly() {
    try {
      await api.post("/reports/generate/weekly");
      await loadData();
    } catch {
      setError("Could not generate weekly report.");
    }
  }

  async function generateMonthly() {
    try {
      await api.post("/reports/generate/monthly");
      await loadData();
    } catch {
      setError("Could not generate monthly report.");
    }
  }

  async function markAsRead(id) {
    try {
      await api.patch(`/reports/${id}/read`);
      await loadData();
    } catch {
      setError("Could not mark report as read.");
    }
  }

  function formatDate(date) {
    if (!date) return "";
    const d = new Date(date);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  }

  function getTrendIcon(trend) {
    if (trend === "increasing") return <TrendingUp size={16} style={{ color: "#dc2626" }} />;
    if (trend === "decreasing") return <TrendingUp size={16} style={{ color: "#16a34a", transform: "rotate(180deg)" }} />;
    return <TrendingUp size={16} style={{ color: "#65738b" }} />;
  }

  if (loading) return <div className="centered">Loading reports...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Financial Reports</h1>
          <p>Automated weekly and monthly spending insights</p>
        </div>
        <div className="header-actions">
          <button className="secondary" onClick={generateWeekly}>
            <FileText size={16} />
            Weekly Report
          </button>
          <button className="secondary" onClick={generateMonthly}>
            <FileText size={16} />
            Monthly Report
          </button>
        </div>
      </header>

      {summary && (
        <section className="panel summary-panel">
          <h2>Report Summary</h2>
          <div className="summary-grid">
            <div className="summary-card">
              <div className="summary-icon">
                <FileText size={24} />
              </div>
              <div className="summary-content">
                <span className="summary-label">Total Reports</span>
                <span className="summary-value">{summary.total_reports}</span>
              </div>
            </div>

            <div className="summary-card">
              <div className="summary-icon">
                <DollarSign size={24} />
              </div>
              <div className="summary-content">
                <span className="summary-label">Avg Monthly Spending</span>
                <span className="summary-value">{currency(summary.average_monthly_spending)}</span>
              </div>
            </div>

            <div className="summary-card">
              <div className="summary-icon">
                <Target size={24} />
              </div>
              <div className="summary-content">
                <span className="summary-label">Avg Savings Rate</span>
                <span className="summary-value">{summary.average_savings_rate.toFixed(1)}%</span>
              </div>
            </div>

            <div className="summary-card">
              <div className="summary-icon">
                {getTrendIcon(summary.spending_trend)}
              </div>
              <div className="summary-content">
                <span className="summary-label">Spending Trend</span>
                <span className="summary-value" style={{ textTransform: "capitalize" }}>
                  {summary.spending_trend}
                </span>
              </div>
            </div>
          </div>
        </section>
      )}

      <section className="panel">
        <div className="panel-header">
          <h2>Your Reports ({reports.length})</h2>
          <div className="filter-buttons">
            <button
              className={`filter-btn ${filter === "all" ? "active" : ""}`}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              className={`filter-btn ${filter === "weekly" ? "active" : ""}`}
              onClick={() => setFilter("weekly")}
            >
              Weekly
            </button>
            <button
              className={`filter-btn ${filter === "monthly" ? "active" : ""}`}
              onClick={() => setFilter("monthly")}
            >
              Monthly
            </button>
          </div>
        </div>

        {reports.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} />
            <p>No reports yet. Generate your first weekly or monthly report to see insights.</p>
          </div>
        ) : (
          <div className="reports-list">
            {reports.map((report) => (
              <div
                key={report.id}
                className={`report-card ${!report.is_read ? "unread" : "read"}`}
                onClick={() => setSelectedReport(selectedReport?.id === report.id ? null : report)}
              >
                <div className="report-header">
                  <div className="report-title">
                    <FileText size={20} />
                    <div>
                      <strong>{report.report_type === "weekly" ? "Weekly" : "Monthly"} Report</strong>
                      <span className="report-date">
                        {formatDate(report.period_start)} - {formatDate(report.period_end)}
                      </span>
                    </div>
                  </div>
                  <div className="report-meta">
                    <span className={`report-type-badge ${report.report_type}`}>
                      {report.report_type}
                    </span>
                    {!report.is_read && <span className="unread-badge">New</span>}
                  </div>
                </div>

                <div className="report-stats">
                  <div className="report-stat">
                    <span className="stat-label">Spending</span>
                    <span className="stat-value">{currency(report.total_spending)}</span>
                  </div>
                  <div className="report-stat">
                    <span className="stat-label">Savings</span>
                    <span className="stat-value" style={{ color: report.net_savings >= 0 ? "#16a34a" : "#dc2626" }}>
                      {currency(report.net_savings)}
                    </span>
                  </div>
                  <div className="report-stat">
                    <span className="stat-label">Savings Rate</span>
                    <span className="stat-value">{report.savings_rate.toFixed(1)}%</span>
                  </div>
                  {report.health_score && (
                    <div className="report-stat">
                      <span className="stat-label">Health Score</span>
                      <span className="stat-value">{report.health_score}/100</span>
                    </div>
                  )}
                </div>

                {selectedReport?.id === report.id && (
                  <div className="report-details">
                    <div className="report-section">
                      <h3>Insights</h3>
                      <div className="insights-list">
                        {report.insights.map((insight, index) => (
                          <div key={index} className="insight-item">
                            {insight}
                          </div>
                        ))}
                      </div>
                    </div>

                    {report.top_expenses.length > 0 && (
                      <div className="report-section">
                        <h3>Top Expenses</h3>
                        <div className="expenses-list">
                          {report.top_expenses.slice(0, 5).map((expense, index) => (
                            <div key={index} className="expense-item">
                              <span className="expense-description">{expense.description}</span>
                              <span className="expense-category">{expense.category}</span>
                              <span className="expense-amount">{currency(expense.amount)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {report.recommendations.length > 0 && (
                      <div className="report-section">
                        <h3>Recommendations</h3>
                        <div className="recommendations-list">
                          {report.recommendations.map((rec, index) => (
                            <div key={index} className="recommendation-item">
                              <strong>{rec.title}</strong>
                              <p>{rec.message}</p>
                              <span>{rec.action}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {!report.is_read && (
                      <button
                        className="primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          markAsRead(report.id);
                        }}
                      >
                        Mark as Read
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}