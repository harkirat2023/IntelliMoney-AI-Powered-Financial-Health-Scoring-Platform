import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { healthStore } from "../../store/healthStore";
import "./HealthV2.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

const priorityColor = { high: "#ef4444", medium: "#f59e0b", low: "#3b82f6" };
const priorityIcon = { high: "🔴", medium: "🟡", low: "🔵" };

export default function HealthRecommendationsPage() {
  const [data, setData] = useState(healthStore);
  const [filter, setFilter] = useState("all");
  useEffect(() => { healthStore.fetchRecommendations(); return healthStore.subscribe(setData); }, []);

  const recs = (data.recommendations || []).filter((r) => filter === "all" || r.priority === filter);
  const counts = { all: data.recommendations?.length || 0, high: data.recommendations?.filter((r) => r.priority === "high").length || 0, medium: data.recommendations?.filter((r) => r.priority === "medium").length || 0, low: data.recommendations?.filter((r) => r.priority === "low").length || 0 };

  return (
    <motion.div className="health-page" variants={container} initial="hidden" animate="show">
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
        <motion.div className="health-card health-empty" variants={item}>
          <p>No recommendations found. Run a health calculation to generate personalized recommendations.</p>
        </motion.div>
      )}

      <div className="rec-grid">
        {recs.map((r) => (
          <motion.div key={r.id} className="health-card rec-full-card" variants={item} style={{ borderLeft: `4px solid ${priorityColor[r.priority] || "#6b7280"}` }}>
            <div className="rec-header">
              <span className="rec-badge" style={{ background: priorityColor[r.priority] || "#6b7280" }}>{r.priority}</span>
              <span className="rec-category">{r.category}</span>
            </div>
            <h3>{r.title}</h3>
            <p>{r.message}</p>
            <div className="rec-detail">
              <div className="rec-metric-bar">
                <span className="rec-metric-label">{r.metric}</span>
                <div className="rec-bar-track">
                  <div className="rec-bar-fill" style={{ width: `${Math.min(r.current_value || 0, 100)}%` }} />
                </div>
                <span className="rec-current">{r.current_value?.toFixed(1)}%</span>
                <span className="rec-arrow">→</span>
                <span className="rec-target">{r.target_value?.toFixed(1)}%</span>
              </div>
            </div>
            <div className="rec-impact">
              <strong>Impact:</strong> {r.impact}
            </div>
            <div className="rec-action">{r.action}</div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
