import { useEffect, useState } from "react";
import { goalsStore } from "../../store/goalsStore";
import { Lightbulb, Loader } from "lucide-react";

export default function GoalRecommendationsPage() {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    goalsStore.fetchRecommendations().then(() => {
      setRecs(goalsStore.recommendations);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="goals-page">
      <div className="page-header"><h2><Lightbulb size={20} /> Goal Recommendations</h2></div>
      {recs.length === 0 ? (
        <div className="empty-state">
          <Lightbulb size={48} />
          <h3>No recommendations yet</h3>
          <p>Create goals and run recalculate to get personalized recommendations</p>
        </div>
      ) : (
        <div className="rec-list">
          {recs.map((r) => (
            <div key={r.id} className="rec-card" style={{ borderLeftColor: r.priority <= 1 ? "#ef4444" : r.priority <= 2 ? "#f59e0b" : "#8b5cf6" }}>
              <h4>{r.title}</h4>
              <p>{r.description}</p>
              <div className="rec-confidence">
                <span>Confidence: {r.confidence_score}%</span>
                <div className="rec-confidence-bar">
                  <div className="rec-confidence-fill" style={{ width: `${r.confidence_score}%` }} />
                </div>
              </div>
              {r.actionable_steps?.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <p style={{ color: "#6b7280", fontSize: "0.78rem", margin: "0 0 4px" }}>Steps:</p>
                  <ul style={{ margin: 0, paddingLeft: 16, fontSize: "0.82rem", color: "#9ca3af" }}>
                    {r.actionable_steps.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
              <div style={{ marginTop: 8, display: "flex", gap: 16, fontSize: "0.75rem", color: "#6b7280" }}>
                <span>Type: {r.recommendation_type?.replace(/_/g, " ")}</span>
                {r.estimated_impact?.monthly_savings && (
                  <span>Impact: ₹{r.estimated_impact.monthly_savings}/mo</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
