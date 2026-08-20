import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { goalsStore } from "../../store/goalsStore";
import { Target, Plus, RefreshCw, Trophy, TrendingUp, Loader } from "lucide-react";

export default function GoalsOverviewPage() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    goalsStore.fetchGoals().then(() => {
      setGoals(goalsStore.goals);
      setLoading(false);
    });
  }, []);

  const handleRecalculate = useCallback(async () => {
    setRecalculating(true);
    await goalsStore.recalculate();
    await goalsStore.fetchGoals();
    setGoals(goalsStore.goals);
    setRecalculating(false);
  }, []);

  if (loading) return <div className="im-page"><div className="im-skeleton" /></div>;

  const stats = {
    total: goals.length,
    active: goals.filter((g) => g.status === "active" || g.status === "on_track").length,
    completed: goals.filter((g) => g.status === "completed").length,
    atRisk: goals.filter((g) => g.status === "at_risk").length,
  };

  return (
    <div className="im-page">
      <div className="im-page-header">
        <div>
          <h1 className="im-page-title"><Target size={22} style={{ verticalAlign: "-4px" }} /> Financial Goals</h1>
          <p className="im-page-subtitle">Track and grow your savings goals.</p>
        </div>
        <div className="im-header-actions">
          <button className="im-btn im-btn-secondary" onClick={handleRecalculate} disabled={recalculating}>
            <RefreshCw size={14} className={recalculating ? "spin" : ""} /> Recalculate
          </button>
          <button className="im-btn im-btn-primary" onClick={() => navigate("/app/goals/create")}>
            <Plus size={14} /> New Goal
          </button>
        </div>
      </div>

      <div className="im-grid im-grid-4">
        <div className="im-card stat-widget">
          <span className="widget-label">Total Goals</span>
          <div className="im-metric-value" style={{ color: "#8b5cf6" }}>{stats.total}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">Active</span>
          <div className="im-metric-value" style={{ color: "var(--ds-ok-strong)" }}>{stats.active}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">Completed</span>
          <div className="im-metric-value" style={{ color: "#3b82f6" }}>{stats.completed}</div>
        </div>
        <div className="im-card stat-widget">
          <span className="widget-label">At Risk</span>
          <div className="im-metric-value" style={{ color: stats.atRisk > 0 ? "var(--ds-danger-strong)" : "var(--neutral-400)" }}>{stats.atRisk}</div>
        </div>
      </div>

      {goals.length === 0 ? (
        <div className="im-empty">
          <Target size={40} />
          <h3>No financial goals yet</h3>
          <p>Create your first goal to start tracking progress.</p>
          <button className="im-btn im-btn-primary" onClick={() => navigate("/app/goals/create")}>
            <Plus size={14} /> Create Goal
          </button>
        </div>
      ) : (
        <div className="im-grid im-grid-3">
          {goals.map((g) => {
            const pct = g.completion_percentage || 0;
            return (
              <div key={g.id} className="im-card" style={{ cursor: "pointer" }} onClick={() => navigate(`/app/goals/${g.id}`)}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <strong style={{ fontSize: "0.95rem", color: "var(--neutral-800)" }}>{g.name}</strong>
                  <span className="im-badge neutral">{g.goal_type.replace(/_/g, " ")}</span>
                </div>
                <div style={{ display: "flex", gap: 16, marginBottom: 12 }}>
                  <span style={{ fontSize: "0.82rem", color: "var(--neutral-600)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                    <Trophy size={14} /> {g.target_amount?.toLocaleString()}
                  </span>
                  <span style={{ fontSize: "0.82rem", color: "var(--neutral-600)", display: "inline-flex", alignItems: "center", gap: 4 }}>
                    <TrendingUp size={14} /> {g.monthly_contribution?.toLocaleString()}/mo
                  </span>
                </div>
                <div className="im-progress">
                  <div className="im-progress-fill" style={{ width: `${pct}%` }} />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 10 }}>
                  <span style={{ fontSize: "0.82rem", color: "var(--neutral-500)" }}>{pct}% complete · {g.estimated_months > 0 ? `${g.estimated_months} months` : "N/A"}</span>
                  <span className={`im-badge ${g.status === "at_risk" ? "danger" : g.status === "completed" ? "ok" : "neutral"}`}>
                    {g.status.replace(/_/g, " ")}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}