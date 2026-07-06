import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { goalsStore } from "../../store/goalsStore";
import { Target, Plus, RefreshCw, Trophy, TrendingUp, AlertTriangle, Loader } from "lucide-react";

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

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  const stats = {
    total: goals.length,
    active: goals.filter((g) => g.status === "active" || g.status === "on_track").length,
    completed: goals.filter((g) => g.status === "completed").length,
    atRisk: goals.filter((g) => g.status === "at_risk").length,
  };

  return (
    <div className="goals-page">
      <div className="page-header">
        <h2><Target size={22} /> Financial Goals</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn-secondary" onClick={handleRecalculate} disabled={recalculating}>
            <RefreshCw size={16} className={recalculating ? "spin" : ""} /> Recalculate
          </button>
          <button className="btn-primary" onClick={() => navigate("/app/goals/create")}>
            <Plus size={16} /> New Goal
          </button>
        </div>
      </div>

      <div className="goals-stats">
        <div className="goal-stat-card">
          <div className="stat-value" style={{ color: "#8b5cf6" }}>{stats.total}</div>
          <div className="stat-label">Total Goals</div>
        </div>
        <div className="goal-stat-card">
          <div className="stat-value" style={{ color: "#10b981" }}>{stats.active}</div>
          <div className="stat-label">Active</div>
        </div>
        <div className="goal-stat-card">
          <div className="stat-value" style={{ color: "#3b82f6" }}>{stats.completed}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="goal-stat-card">
          <div className="stat-value" style={{ color: stats.atRisk > 0 ? "#ef4444" : "#6b7280" }}>{stats.atRisk}</div>
          <div className="stat-label">At Risk</div>
        </div>
      </div>

      {goals.length === 0 ? (
        <div className="empty-state">
          <Target size={48} />
          <h3>No financial goals yet</h3>
          <p>Create your first goal to start tracking progress</p>
          <button className="btn-primary" onClick={() => navigate("/app/goals/create")}>
            <Plus size={16} /> Create Goal
          </button>
        </div>
      ) : (
        <div className="goal-grid">
          {goals.map((g) => {
            const pct = g.completion_percentage || 0;
            const fillClass = pct >= 80 ? "high" : pct >= 40 ? "medium" : "low";
            return (
              <div key={g.id} className="goal-card" onClick={() => navigate(`/app/goals/${g.id}`)}>
                <div className="goal-card-header">
                  <h3>{g.name}</h3>
                  <span className="goal-type-badge">{g.goal_type.replace(/_/g, " ")}</span>
                </div>
                <div className="goal-card-details">
                  <span><Trophy size={14} /> ₹{g.target_amount?.toLocaleString()}</span>
                  <span><TrendingUp size={14} /> ₹{g.monthly_contribution?.toLocaleString()}/mo</span>
                </div>
                <div className="goal-progress-bar">
                  <div className={`goal-progress-fill ${fillClass}`} style={{ width: `${pct}%` }} />
                </div>
                <div className="goal-card-details">
                  <span>{pct}% complete</span>
                  <span>{g.estimated_months > 0 ? `${g.estimated_months} months` : "N/A"}</span>
                </div>
                <div className="goal-card-footer">
                  <span className={`goal-status ${g.status}`}>{g.status.replace(/_/g, " ")}</span>
                  <span style={{ color: "#6b7280", fontSize: "0.75rem" }}>
                    Score: {g.confidence_score || g.feasibility_score || "—"}
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
