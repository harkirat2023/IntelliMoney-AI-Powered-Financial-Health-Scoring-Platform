import { useEffect, useState } from "react";
import { goalsStore } from "../../store/goalsStore";
import { TrendingUp, Target, Calendar, CheckCircle, XCircle, Loader } from "lucide-react";

export default function GoalProgressPage() {
  const [progressData, setProgressData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    goalsStore.fetchProgress().then(() => {
      setProgressData(goalsStore.progress);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="goals-page">
      <div className="page-header"><h2><TrendingUp size={20} /> Goal Progress Tracking</h2></div>
      {progressData.length === 0 ? (
        <div className="empty-state">
          <TrendingUp size={48} />
          <h3>No progress data yet</h3>
          <p>Active goals will appear here with their progress history</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          {progressData.map((item) => {
            const g = item.goal;
            const pct = g.completion_percentage || 0;
            const fillClass = pct >= 80 ? "high" : pct >= 40 ? "medium" : "low";
            return (
              <div key={g.id} className="detail-card">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <h4 style={{ margin: 0, color: "#f9fafb", display: "flex", alignItems: "center", gap: 8 }}>
                    <Target size={16} /> {g.name}
                  </h4>
                  <span className={`goal-status ${g.status}`}>{g.status.replace(/_/g, " ")}</span>
                </div>
                <div className="goal-progress-bar">
                  <div className={`goal-progress-fill ${fillClass}`} style={{ width: `${pct}%` }} />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem", color: "#9ca3af", marginBottom: 16 }}>
                  <span>₹{g.current_amount?.toLocaleString()} / ₹{g.target_amount?.toLocaleString()}</span>
                  <span>{pct}% complete</span>
                </div>
                {item.progress?.length > 0 && (
                  <div>
                    <p style={{ fontSize: "0.82rem", color: "#6b7280", margin: "0 0 8px" }}>Period History</p>
                    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                      {item.progress.slice(0, 12).map((p) => (
                        <div key={p.id || p.period} style={{
                          display: "flex", justifyContent: "space-between", alignItems: "center",
                          padding: "6px 10px", background: "#111827", borderRadius: 6, fontSize: "0.8rem",
                        }}>
                          <span style={{ color: "#9ca3af" }}>{p.period}</span>
                          <span style={{ color: "#d1d5db" }}>₹{p.current_amount?.toLocaleString()}</span>
                          <span style={{ color: p.on_track ? "#10b981" : "#ef4444", display: "flex", alignItems: "center", gap: 4 }}>
                            {p.on_track ? <CheckCircle size={12} /> : <XCircle size={12} />}
                            {p.on_track ? "On Track" : "Missed"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
