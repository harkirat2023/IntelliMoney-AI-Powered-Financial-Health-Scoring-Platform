import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { budgetIntelligenceStore } from "../../../store/budgetIntelligenceStore";
import { StatWidget } from "../../../dashboard/widgets/StatWidget";
import "../../layouts/BudgetIntelligenceLayout.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function BIOptimizationPage() {
  const [data, setData] = useState(budgetIntelligenceStore);
  useEffect(() => { budgetIntelligenceStore.fetchOptimization(); return budgetIntelligenceStore.subscribe(setData); }, []);

  const opt = data.optimization;
  const suggestions = opt?.suggestions || [];

  return (
    <motion.div className="bi-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Budget Optimization</h1>
        <button className="btn btn-primary btn-sm" onClick={() => budgetIntelligenceStore.fetchOptimization()}>
          Refresh
        </button>
      </motion.div>

      {!opt && (
        <motion.div className="bi-card" variants={item} style={{ textAlign: "center", color: "#6b7280", padding: 40 }}>
          No optimization data available. Run a budget intelligence generation first.
        </motion.div>
      )}

      {opt && (
        <>
          <motion.div className="bi-stats-row" variants={item}>
            <StatWidget label="Current Budget" value={opt.total_current || 0} change={0} prefix="₹" />
            <StatWidget label="Suggested Budget" value={opt.total_suggested || 0} change={0} prefix="₹" />
            <StatWidget label="Monthly Savings" value={opt.potential_monthly_savings || 0} change={0} prefix="₹" />
            <StatWidget label="Categories" value={suggestions.length} change={0} />
          </motion.div>

          {opt.insights?.length > 0 && (
            <motion.div className="bi-card" variants={item}>
              <h3>Insights</h3>
              <ul className="bi-insights">
                {opt.insights.map((insight, i) => <li key={i}>{insight}</li>)}
              </ul>
            </motion.div>
          )}

          <motion.div variants={item}>
            <h3 style={{ color: "#f9fafb", margin: "16px 0 12px", fontSize: "1rem" }}>Category Suggestions</h3>
            <div className="bi-opt-grid">
              {suggestions.map((s) => (
                <div key={s.category} className="bi-opt-card">
                  <div className="opt-category">{s.category}</div>
                  <div className="opt-limits">
                    <span className="current">₹{s.current_limit}</span>
                    <span style={{ color: "#6b7280" }}>→</span>
                    <span className="suggested">₹{s.suggested_limit}</span>
                  </div>
                  <div className="opt-reason">{s.reason}</div>
                  {s.potential_savings > 0 && (
                    <div style={{ fontSize: "0.85rem", color: "#10b981", fontWeight: 600, marginTop: 6 }}>
                      Save ₹{s.potential_savings}/mo
                    </div>
                  )}
                  <div style={{ fontSize: "0.72rem", color: "#6b7280", marginTop: 4 }}>
                    Confidence: {(s.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </motion.div>
  );
}
