import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { budgetIntelligenceStore } from "../../store/budgetIntelligenceStore";
import  StatWidget  from "../../dashboard/widgets/StatWidget";
import "../../layouts/BudgetIntelligenceLayout.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.07 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

const scoreColor = (s) => s >= 80 ? "excellent" : s >= 65 ? "good" : s >= 45 ? "moderate" : "needs-attention";
const barColor = (pct) => pct > 100 ? "#ef4444" : pct > 80 ? "#f59e0b" : "#10b981";

export default function BIOOverviewPage() {
  const [data, setData] = useState(budgetIntelligenceStore);
  useEffect(() => { budgetIntelligenceStore.fetchAll(); return budgetIntelligenceStore.subscribe(setData); }, []);

  const current = data.current;
  const recs = data.recommendations?.slice(0, 5) || [];
  const opps = data.opportunities?.slice(0, 4) || [];
  const risk = data.risk;
  const score = current?.budget_score || 0;
  const sClass = scoreColor(score);
  const deg = (score / 100) * 360;

  return (
    <motion.div className="bi-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Budget Intelligence</h1>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => budgetIntelligenceStore.generate()} disabled={data.loading.generate}>
            {data.loading.generate ? "Generating..." : "Generate"}
          </button>
          <button className="btn btn-outline" onClick={() => budgetIntelligenceStore.recalculate()} disabled={data.loading.generate}>
            Recalculate
          </button>
        </div>
      </motion.div>

      <motion.div className="bi-stats-row" variants={item}>
        <StatWidget label="Budget Score" value={score} change={0} suffix="" />
        <StatWidget label="Potential Savings" value={current?.potential_savings || 0} change={0} prefix="₹" />
        <StatWidget label="Risk Level" value={risk?.overall_risk_level || "N/A"} change={0} />
        <StatWidget label="Categories" value={current?.category_count || 0} change={0} />
      </motion.div>

      <motion.div className="bi-grid" variants={item}>
        <div className="bi-card" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <h3>Budget Score</h3>
          <div className={`bi-score-ring ${sClass}`} style={{"--deg": `${deg}deg`}}>
            <div className="bi-score-ring-inner">
              <span>{score}</span>
              <span>{risk?.overall_risk_level || "N/A"}</span>
            </div>
          </div>
        </div>

        <div className="bi-card">
          <h3>Category Breakdown ({current?.category_count || 0})</h3>
          <div className="bi-category-strip">
            {(current?.categories || []).slice(0, 12).map((c) => (
              <div key={c.category} className="bi-category-row">
                <span className="bi-category-name">{c.category}</span>
                <div className="bi-category-bar">
                  <div className="bi-category-fill" style={{ width: `${Math.min(c.percentage_used, 100)}%`, background: barColor(c.percentage_used) }} />
                </div>
                <span className="bi-category-pct" style={{ color: barColor(c.percentage_used) }}>{c.percentage_used}%</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {recs.length > 0 && (
        <motion.div className="bi-card" variants={item}>
          <h3>Top Recommendations</h3>
          <div className="bi-rec-strip">
            {recs.map((r) => (
              <div key={r.id} className={`bi-rec-item ${r.priority}`}>
                <div className="rec-label">{r.priority} priority · {r.category}</div>
                <div className="rec-title">{r.title}</div>
                <div className="rec-message">{r.message}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {opps.length > 0 && (
        <motion.div className="bi-card" variants={item}>
          <h3>Savings Opportunities</h3>
          <div className="bi-opp-grid">
            {opps.map((o) => (
              <div key={o.id} className="bi-opp-card">
                <div className="opp-header">
                  <strong>{o.title}</strong>
                  <span className="opp-savings">₹{o.potential_savings}/mo</span>
                </div>
                <div className="opp-message">{o.message}</div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
