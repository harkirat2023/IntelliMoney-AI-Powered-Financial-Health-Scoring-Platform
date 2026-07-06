import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { goalsStore } from "../../store/goalsStore";
import { PlusCircle, Loader, CheckCircle, XCircle } from "lucide-react";

const GOAL_TYPES = [
  { value: "emergency_fund", label: "Emergency Fund" },
  { value: "vacation", label: "Vacation" },
  { value: "laptop", label: "Laptop" },
  { value: "vehicle", label: "Vehicle" },
  { value: "house", label: "House" },
  { value: "education", label: "Education" },
  { value: "wedding", label: "Wedding" },
  { value: "retirement", label: "Retirement" },
  { value: "investment", label: "Investment" },
  { value: "custom", label: "Custom" },
];

export default function CreateGoalPage() {
  const [form, setForm] = useState({
    goal_type: "custom", name: "", target_amount: "",
    current_amount: "0", monthly_contribution: "0",
    target_date: "", priority: "medium", description: "",
    auto_adjust: true,
  });
  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [creating, setCreating] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleAnalyze = async () => {
    if (!form.name || !form.target_amount) return;
    setAnalyzing(true);
    try {
      const result = await goalsStore.analyze({
        goal_type: form.goal_type, name: form.name,
        target_amount: parseFloat(form.target_amount),
        target_date: form.target_date,
        monthly_contribution: parseFloat(form.monthly_contribution) || 0,
      });
      setAnalysis(result);
    } catch { }
    finally { setAnalyzing(false); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const data = {
        ...form,
        target_amount: parseFloat(form.target_amount),
        current_amount: parseFloat(form.current_amount) || 0,
        monthly_contribution: parseFloat(form.monthly_contribution) || 0,
      };
      const result = await goalsStore.createGoal(data);
      navigate(`/app/goals/${result.goal.id}`);
    } catch { }
    finally { setCreating(false); }
  };

  return (
    <div className="goals-page">
      <div className="page-header"><h2><PlusCircle size={20} /> Create Financial Goal</h2></div>

      <div className="goal-form">
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label>Goal Type</label>
              <select name="goal_type" value={form.goal_type} onChange={handleChange}>
                {GOAL_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select name="priority" value={form.priority} onChange={handleChange}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Goal Name</label>
            <input name="name" value={form.name} onChange={handleChange} placeholder="e.g., New MacBook Pro" required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Target Amount (₹)</label>
              <input name="target_amount" type="number" min="1" value={form.target_amount}
                onChange={handleChange} placeholder="120000" required />
            </div>
            <div className="form-group">
              <label>Current Savings (₹)</label>
              <input name="current_amount" type="number" min="0" value={form.current_amount}
                onChange={handleChange} placeholder="0" />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Monthly Contribution (₹)</label>
              <input name="monthly_contribution" type="number" min="0" value={form.monthly_contribution}
                onChange={handleChange} placeholder="0 — auto-calculated" />
            </div>
            <div className="form-group">
              <label>Target Date</label>
              <input name="target_date" type="date" value={form.target_date} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={form.description} onChange={handleChange} placeholder="Optional notes..." />
          </div>

          <div className="form-group">
            <label>
              <input type="checkbox" name="auto_adjust" checked={form.auto_adjust} onChange={handleChange} />
              {" "}Auto-adjust savings plan based on financial changes
            </label>
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
            <button type="button" className="btn-secondary" onClick={handleAnalyze} disabled={analyzing}>
              {analyzing ? <Loader className="spin" size={16} /> : null} Analyze Feasibility
            </button>
            <button type="submit" className="btn-primary" disabled={creating}>
              {creating ? <Loader className="spin" size={16} /> : <PlusCircle size={16} />} Create Goal
            </button>
          </div>
        </form>

        {analysis && (
          <div className="analysis-result">
            <h3>Feasibility Analysis</h3>
            <div className="analysis-grid">
              <div className="analysis-item">
                <span className="label">Feasible</span>
                <span className={`value ${analysis.feasible ? "feasible" : "not-feasible"}`}>
                  {analysis.feasible ? <CheckCircle size={16} /> : <XCircle size={16} />} {analysis.feasible ? "Yes" : "No"}
                </span>
              </div>
              <div className="analysis-item">
                <span className="label">Feasibility Score</span>
                <span className="value">{analysis.feasibility_score}/100</span>
              </div>
              <div className="analysis-item">
                <span className="label">Affordability</span>
                <span className="value">{analysis.affordability_score}/100</span>
              </div>
              <div className="analysis-item">
                <span className="label">Estimated Months</span>
                <span className="value">{analysis.estimated_months}</span>
              </div>
              <div className="analysis-item">
                <span className="label">Monthly Savings Required</span>
                <span className="value">₹{analysis.monthly_savings_required?.toLocaleString()}</span>
              </div>
              <div className="analysis-item">
                <span className="label">Risk Level</span>
                <span className="value" style={{ textTransform: "capitalize" }}>{analysis.risk_level}</span>
              </div>
              <div className="analysis-item">
                <span className="label">Confidence</span>
                <span className="value">{analysis.confidence_score}%</span>
              </div>
            </div>
            {analysis.suggestions?.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ color: "#f59e0b", margin: "0 0 8px" }}>Suggestions</h4>
                <ul style={{ color: "#9ca3af", fontSize: "0.85rem", margin: 0, paddingLeft: 20 }}>
                  {analysis.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
