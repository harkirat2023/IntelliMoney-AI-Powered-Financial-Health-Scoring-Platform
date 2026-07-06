import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { goalsStore } from "../../store/goalsStore";
import { Clock, CheckCircle, XCircle, Loader } from "lucide-react";

const STATUS_FILTERS = ["all", "completed", "cancelled", "paused"];

export default function GoalHistoryPage() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const navigate = useNavigate();

  useEffect(() => {
    goalsStore.fetchGoals().then(() => {
      setGoals(goalsStore.goals);
      setLoading(false);
    });
  }, []);

  const getStatusGoals = () => {
    if (filter === "all") return goals;
    return goals.filter((g) => g.status === filter);
  };

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  const displayed = getStatusGoals();

  return (
    <div className="goals-page">
      <div className="page-header">
        <h2><Clock size={20} /> Goal History</h2>
        <div style={{ display: "flex", gap: 6 }}>
          {STATUS_FILTERS.map((f) => (
            <button key={f} className={`btn-secondary ${filter === f ? "active-filter" : ""}`}
              style={filter === f ? { borderColor: "#8b5cf6", color: "#f9fafb" } : {}}
              onClick={() => setFilter(f)}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>
      {displayed.length === 0 ? (
        <div className="empty-state">
          <Clock size={48} />
          <h3>No {filter !== "all" ? filter : ""} goals found</h3>
        </div>
      ) : (
        <div className="goal-grid">
          {displayed.map((g) => (
            <div key={g.id} className="goal-card" onClick={() => navigate(`/app/goals/${g.id}`)}>
              <div className="goal-card-header">
                <h3>{g.name}</h3>
                <span style={{ color: g.status === "completed" ? "#10b981" : "#ef4444", display: "flex", alignItems: "center", gap: 4, fontSize: "0.82rem" }}>
                  {g.status === "completed" ? <CheckCircle size={14} /> : <XCircle size={14} />}
                  {g.status}
                </span>
              </div>
              <div className="goal-card-details">
                <span>₹{g.target_amount?.toLocaleString()}</span>
                <span>{g.completion_percentage || 0}%</span>
              </div>
              <div className="goal-progress-bar">
                <div className="goal-progress-fill" style={{ width: `${g.completion_percentage || 0}%`, background: g.status === "completed" ? "#8b5cf6" : "#6b7280" }} />
              </div>
              <div className="goal-card-footer">
                <span className={`goal-status ${g.status}`}>{g.status.replace(/_/g, " ")}</span>
                <span style={{ color: "#6b7280", fontSize: "0.75rem" }}>
                  {g.estimated_months > 0 ? `${g.estimated_months}mo` : "—"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
