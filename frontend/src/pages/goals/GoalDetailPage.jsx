import { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { goalsStore } from "../../store/goalsStore";
import { ArrowLeft, Edit3, Trash2, Target, Calendar, TrendingUp, Loader } from "lucide-react";

export default function GoalDetailPage() {
  const { goalId } = useParams();
  const [goal, setGoal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    goalsStore.fetchGoal(goalId).then(() => {
      setGoal(goalsStore.currentGoal);
      setLoading(false);
    });
  }, [goalId]);

  const handleDelete = useCallback(async () => {
    if (!window.confirm("Delete this goal?")) return;
    await goalsStore.deleteGoal(goalId);
    navigate("/app/goals");
  }, [goalId, navigate]);

  const handleUpdate = useCallback(async () => {
    await goalsStore.updateGoal(goalId, editForm);
    setGoal(goalsStore.currentGoal);
    setEditing(false);
  }, [goalId, editForm]);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;
  if (!goal) return <div className="empty-state"><Target size={48} /><p>Goal not found</p></div>;

  const pct = goal.completion_percentage || 0;
  const ringClass = pct >= 100 ? "complete" : pct >= 80 ? "high" : pct >= 40 ? "medium" : "low";
  const deg = pct >= 100 ? 360 : (pct / 100) * 360;

  return (
    <div className="goal-detail-page">
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <button className="btn-ghost" onClick={() => navigate("/app/goals")}><ArrowLeft size={18} /> Back</button>
      </div>

      <div className="goal-detail-header">
        <h2>{goal.name}</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn-secondary" onClick={() => { setEditing(!editing); setEditForm({}); }}>
            <Edit3 size={16} /> Edit
          </button>
          <button className="btn-secondary" style={{ color: "#ef4444" }} onClick={handleDelete}>
            <Trash2 size={16} /> Delete
          </button>
        </div>
      </div>

      <div className="goal-detail-progress">
        <div className="big-progress">
          <div className={`progress-ring ${ringClass}`} style={{ "--deg": `${deg}deg` }}>
            <span>{Math.round(pct)}%</span>
          </div>
          <div className="progress-details">
            <div className="amount">₹{goal.current_amount?.toLocaleString()} / ₹{goal.target_amount?.toLocaleString()}</div>
            <div className="sub"><Calendar size={14} /> {goal.estimated_months > 0 ? `~${goal.estimated_months} months remaining` : "No estimate"}</div>
            <div className="sub"><TrendingUp size={14} /> ₹{goal.monthly_contribution?.toLocaleString()}/month</div>
            <span className={`goal-status ${goal.status}`} style={{ marginTop: 4, display: "inline-block" }}>
              {goal.status?.replace(/_/g, " ")}
            </span>
          </div>
        </div>
      </div>

      {editing && (
        <div className="detail-card" style={{ marginBottom: 20 }}>
          <h4>Edit Goal</h4>
          <div className="form-row">
            <div className="form-group">
              <label>Target Amount</label>
              <input type="number" defaultValue={goal.target_amount}
                onChange={(e) => setEditForm({ ...editForm, target_amount: parseFloat(e.target.value) || 0 })}
                placeholder={String(goal.target_amount)} />
            </div>
            <div className="form-group">
              <label>Current Amount</label>
              <input type="number" defaultValue={goal.current_amount}
                onChange={(e) => setEditForm({ ...editForm, current_amount: parseFloat(e.target.value) || 0 })}
                placeholder={String(goal.current_amount)} />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Monthly Contribution</label>
              <input type="number" defaultValue={goal.monthly_contribution}
                onChange={(e) => setEditForm({ ...editForm, monthly_contribution: parseFloat(e.target.value) || 0 })}
                placeholder={String(goal.monthly_contribution)} />
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select defaultValue={goal.priority}
                onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Status</label>
            <select defaultValue={goal.status}
              onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}>
              <option value="active">Active</option>
              <option value="on_track">On Track</option>
              <option value="at_risk">At Risk</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <button className="btn-primary" onClick={handleUpdate}>Save Changes</button>
        </div>
      )}

      <div className="goal-detail-grid">
        <div className="detail-card">
          <h4>Goal Details</h4>
          <div className="detail-row"><span className="label">Type</span><span className="value" style={{ textTransform: "capitalize" }}>{goal.goal_type?.replace(/_/g, " ")}</span></div>
          <div className="detail-row"><span className="label">Target</span><span className="value">₹{goal.target_amount?.toLocaleString()}</span></div>
          <div className="detail-row"><span className="label">Current</span><span className="value">₹{goal.current_amount?.toLocaleString()}</span></div>
          <div className="detail-row"><span className="label">Monthly</span><span className="value">₹{goal.monthly_contribution?.toLocaleString()}</span></div>
          <div className="detail-row"><span className="label">Target Date</span><span className="value">{goal.target_date || "Flexible"}</span></div>
          <div className="detail-row"><span className="label">Priority</span><span className="value" style={{ textTransform: "capitalize" }}>{goal.priority}</span></div>
        </div>
        <div className="detail-card">
          <h4>Feasibility</h4>
          <div className="detail-row"><span className="label">Feasibility Score</span><span className="value">{goal.feasibility_score}/100</span></div>
          <div className="detail-row"><span className="label">Affordability</span><span className="value">{goal.affordability_score}/100</span></div>
          <div className="detail-row"><span className="label">Confidence</span><span className="value">{goal.confidence_score}%</span></div>
          <div className="detail-row"><span className="label">Risk Level</span><span className="value" style={{ textTransform: "capitalize" }}>{goal.risk_level}</span></div>
          <div className="detail-row"><span className="label">Est. Months</span><span className="value">{goal.estimated_months || "N/A"}</span></div>
          <div className="detail-row"><span className="label">Auto Adjust</span><span className="value">{goal.auto_adjust ? "Enabled" : "Disabled"}</span></div>
        </div>
      </div>

      {goal.description && (
        <div className="detail-card" style={{ marginTop: 16 }}>
          <h4>Description</h4>
          <p style={{ color: "#9ca3af", fontSize: "0.85rem", margin: 0 }}>{goal.description}</p>
        </div>
      )}
    </div>
  );
}
