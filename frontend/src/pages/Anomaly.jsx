import { useEffect, useState } from "react";
import { AlertTriangle, Bell, Check, RefreshCw, TrendingUp } from "lucide-react";

import { api } from "../api/client";
import { currency } from "../utils/format";

const severityColors = {
  low: "#3b82f6",
  medium: "#f59e0b",
  high: "#f97316",
  critical: "#dc2626"
};

const severityLabels = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical"
};

export default function Anomaly() {
  const [anomalies, setAnomalies] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("anomalies"); // anomalies, alerts, report

  async function loadData() {
    try {
      const [anomaliesRes, alertsRes, reportRes] = await Promise.all([
        api.get("/anomaly"),
        api.get("/anomaly/alerts"),
        api.get("/anomaly/weekly-report"),
      ]);
      setAnomalies(anomaliesRes.data);
      setAlerts(alertsRes.data);
      setWeeklyReport(reportRes.data);
    } catch {
      setError("Could not load anomaly data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function runDetection() {
    try {
      await api.post("/anomaly/detect");
      await loadData();
    } catch {
      setError("Could not run anomaly detection.");
    }
  }

  async function markAsRead(id) {
    try {
      await api.patch(`/anomaly/${id}/read`);
      await loadData();
    } catch {
      setError("Could not mark anomaly as read.");
    }
  }

  function formatDate(date) {
    if (!date) return "";
    const d = new Date(date);
    return d.toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
  }

  function getSeverityIcon(severity) {
    const color = severityColors[severity];
    return <AlertTriangle size={18} style={{ color }} />;
  }

  if (loading) return <div className="centered">Loading anomaly detection...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Spending Anomaly Detection</h1>
          <p>ML-powered alerts for unusual spending patterns</p>
        </div>
        <button className="secondary" onClick={runDetection}>
          <RefreshCw size={16} />
          Run Detection
        </button>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === "anomalies" ? "active" : ""}`}
          onClick={() => setActiveTab("anomalies")}
        >
          <AlertTriangle size={16} />
          Anomalies ({anomalies.length})
        </button>
        <button
          className={`tab ${activeTab === "alerts" ? "active" : ""}`}
          onClick={() => setActiveTab("alerts")}
        >
          <Bell size={16} />
          Alerts ({alerts.length})
        </button>
        <button
          className={`tab ${activeTab === "report" ? "active" : ""}`}
          onClick={() => setActiveTab("report")}
        >
          <TrendingUp size={16} />
          Weekly Report
        </button>
      </div>

      {activeTab === "anomalies" && (
        <section className="panel">
          <h2>Detected Anomalies</h2>
          {anomalies.length === 0 ? (
            <div className="empty-state">
              <TrendingUp size={48} />
              <p>No anomalies detected yet. Click "Run Detection" to analyze your spending patterns.</p>
            </div>
          ) : (
            <div className="anomaly-list">
              {anomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  className={`anomaly-card ${anomaly.is_read ? "read" : "unread"} severity-${anomaly.severity}`}
                >
                  <div className="anomaly-header">
                    <div className="anomaly-title">
                      {getSeverityIcon(anomaly.severity)}
                      <div>
                        <strong>{anomaly.category}</strong>
                        <span className="severity-badge" style={{ background: severityColors[anomaly.severity] }}>
                          {severityLabels[anomaly.severity]}
                        </span>
                      </div>
                    </div>
                    {!anomaly.is_read && (
                      <button
                        className="icon-button"
                        onClick={() => markAsRead(anomaly.id)}
                        aria-label="Mark as read"
                      >
                        <Check size={16} />
                      </button>
                    )}
                  </div>
                  <div className="anomaly-body">
                    <div className="anomaly-stats">
                      <div className="stat-item">
                        <span className="stat-label">Amount Spent</span>
                        <span className="stat-value">{currency(anomaly.amount)}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Average</span>
                        <span className="stat-value">{currency(anomaly.average_amount)}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Deviation</span>
                        <span className="stat-value" style={{ color: severityColors[anomaly.severity] }}>
                          +{anomaly.deviation_percentage.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <p className="anomaly-message">{anomaly.message}</p>
                    <small className="anomaly-date">{formatDate(anomaly.date)}</small>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "alerts" && (
        <section className="panel">
          <h2>Active Alerts</h2>
          {alerts.length === 0 ? (
            <div className="empty-state">
              <Bell size={48} />
              <p>No active alerts. Great job maintaining healthy spending habits!</p>
            </div>
          ) : (
            <div className="alerts-list">
              {alerts.map((alert, index) => (
                <div key={index} className={`alert-card severity-${alert.severity}`}>
                  <div className="alert-header">
                    <AlertTriangle size={18} style={{ color: severityColors[alert.severity] }} />
                    <strong>{alert.category}</strong>
                    <span className="severity-badge" style={{ background: severityColors[alert.severity] }}>
                      {severityLabels[alert.severity]}
                    </span>
                  </div>
                  <p className="alert-message">{alert.message}</p>
                  <div className="alert-suggestion">
                    <strong>💡 Suggestion:</strong> {alert.suggestion}
                  </div>
                  <small className="alert-date">{formatDate(alert.date)}</small>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {activeTab === "report" && weeklyReport && (
        <section className="panel">
          <h2>Weekly Spending Report</h2>
          <div className="report-header">
            <div className="report-dates">
              <span>{formatDate(weeklyReport.week_start)}</span>
              <span>to</span>
              <span>{formatDate(weeklyReport.week_end)}</span>
            </div>
            {weeklyReport.comparison_to_previous_week !== null && (
              <div className={`comparison-badge ${weeklyReport.comparison_to_previous_week > 0 ? "increase" : "decrease"}`}>
                <TrendingUp size={16} />
                {weeklyReport.comparison_to_previous_week > 0 ? "+" : ""}
                {weeklyReport.comparison_to_previous_week}% vs last week
              </div>
            )}
          </div>

          <div className="report-stats">
            <div className="report-stat">
              <span className="report-stat-label">Total Spending</span>
              <span className="report-stat-value">{currency(weeklyReport.total_spending)}</span>
            </div>
            <div className="report-stat">
              <span className="report-stat-label">Anomalies Detected</span>
              <span className="report-stat-value" style={{ color: weeklyReport.anomalies_detected > 0 ? "#dc2626" : "#16a34a" }}>
                {weeklyReport.anomalies_detected}
              </span>
            </div>
          </div>

          {weeklyReport.top_categories.length > 0 && (
            <div className="top-categories">
              <h3>Top Categories</h3>
              <div className="category-list">
                {weeklyReport.top_categories.map((cat, index) => (
                  <div key={index} className="category-item">
                    <span className="category-rank">#{index + 1}</span>
                    <span className="category-name">{cat.category}</span>
                    <span className="category-amount">{currency(cat.amount)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="insights">
            <h3>Insights</h3>
            <div className="insights-list">
              {weeklyReport.insights.map((insight, index) => (
                <div key={index} className="insight-item">
                  {insight}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}