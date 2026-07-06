import { motion } from "framer-motion";

const LEVEL_COLORS = {
  Excellent: { bg: "#ecfdf5", text: "#166534", border: "#bbf7d0" },
  Good: { bg: "#eff6ff", text: "#1e40af", border: "#bfdbfe" },
  Moderate: { bg: "#fffbeb", text: "#92400e", border: "#fde68a" },
  "Needs Attention": { bg: "#fef2f2", text: "#991b1b", border: "#fecaca" },
};

export default function HealthScoreWidget({ data }) {
  if (!data) return null;
  const colors = LEVEL_COLORS[data.risk_level] || LEVEL_COLORS["Needs Attention"];

  return (
    <article className="dash-widget health-widget" style={{ borderColor: colors.border, background: colors.bg }}>
      <div className="widget-header">
        <span className="widget-label">Financial Health</span>
        <span className="widget-badge" style={{ background: colors.border, color: colors.text }}>{data.trend}</span>
      </div>
      <div className="health-score-display">
        <motion.div
          className="health-score-number"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 12 }}
          style={{ color: colors.text }}
        >
          {data.score}
          <span className="health-score-max">/100</span>
        </motion.div>
      </div>
      <div className="health-score-label" style={{ color: colors.text }}>{data.risk_level}</div>
      <div className="health-factors">
        <div className="health-factor">
          <span className="factor-label">Savings</span>
          <div className="factor-bar"><span style={{ width: `${data.savings_rate}%` }} /></div>
        </div>
        <div className="health-factor">
          <span className="factor-label">Budget</span>
          <div className="factor-bar"><span style={{ width: `${data.budget_adherence}%` }} /></div>
        </div>
        <div className="health-factor">
          <span className="factor-label">Stability</span>
          <div className="factor-bar"><span style={{ width: `${data.expense_stability}%` }} /></div>
        </div>
      </div>
    </article>
  );
}
