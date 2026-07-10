import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { budgetIntelligenceStore } from "../../store/budgetIntelligenceStore";
import "../../layouts/BudgetIntelligenceLayout.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const priorityColor = { high: "#ef4444", medium: "#f59e0b", low: "#3b82f6" };

export default function BIRecommendationsPage() {
  const [data, setData] = useState(budgetIntelligenceStore);
  const [filter, setFilter] = useState("all");
  useEffect(() => { budgetIntelligenceStore.fetchRecommendations(); return budgetIntelligenceStore.subscribe(setData); }, []);

  const recs = (data.recommendations || []).filter((r) => filter === "all" || r.priority === filter);
  const counts = ["all", "high", "medium", "low"].reduce((acc, p) => { acc[p] = p === "all" ? (data.recommendations?.length || 0) : data.recommendations?.filter((r) => r.priority === p).length || 0; return acc; }, {});

  return (
    <motion.div className="bi-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Recommendations</h1>
        <div className="rec-filters">
          {["all", "high", "medium", "low"].map((p) => (
            <button key={p} className={`btn btn-sm ${filter === p ? "btn-primary" : "btn-outline"}`} onClick={() => setFilter(p)}>
              {p.charAt(0).toUpperCase() + p.slice(1)} ({counts[p]})
            </button>
          ))}
        </div>
      </motion.div>

      {recs.length === 0 && (
        <motion.div className="bi-card" variants={item} style={{ textAlign: "center", color: "#6b7280", padding: 40 }}>
          No recommendations found. Run a budget intelligence generation first.
        </motion.div>
      )}

      <div className="rec-grid">
        {recs.map((r) => (
          <motion.div key={r.id} className="bi-card rec-full-card" variants={item} style={{ borderLeft: `4px solid ${priorityColor[r.priority] || "#6b7280"}` }}>
            <div className="rec-header">
              <span className="rec-badge" style={{ background: priorityColor[r.priority] || "#6b7280" }}>{r.priority}</span>
              <span className="rec-category">{r.category} · {r.recommendation_type}</span>
            </div>
            <h3 style={{ fontSize: "0.9rem", margin: "6px 0" }}>{r.title}</h3>
            <p style={{ fontSize: "0.82rem", color: "#9ca3af", lineHeight: 1.4 }}>{r.message}</p>
            <div className="rec-detail">
              <div className="rec-metric-bar">
                <span className="rec-metric-label">{r.recommendation_type}</span>
                <div className="rec-bar-track">
                  <div className="rec-bar-fill" style={{ width: `${Math.min(r.confidence_score * 100, 100)}%`, background: priorityColor[r.priority] }} />
                </div>
                <span style={{ fontSize: "0.75rem", color: "#9ca3af" }}>{(r.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </div>
            {r.potential_savings > 0 && (
              <div style={{ fontSize: "0.85rem", color: "#10b981", fontWeight: 600 }}>₹{r.potential_savings}/mo savings</div>
            )}
            <div style={{ fontSize: "0.78rem", color: "#d1d5db", marginTop: 4 }}>{r.estimated_impact}</div>
            <div style={{ fontSize: "0.78rem", color: "#3b82f6", fontStyle: "italic", marginTop: 6, padding: "6px 8px", background: "rgba(59,130,246,0.08)", borderRadius: 6 }}>
              {r.actionable_steps?.[0] || r.reasoning}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
