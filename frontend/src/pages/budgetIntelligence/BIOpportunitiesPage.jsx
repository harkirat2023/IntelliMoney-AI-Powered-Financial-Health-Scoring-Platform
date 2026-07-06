import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { budgetIntelligenceStore } from "../../../store/budgetIntelligenceStore";
import { StatWidget } from "../../../dashboard/widgets/StatWidget";
import "../../layouts/BudgetIntelligenceLayout.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function BIOpportunitiesPage() {
  const [data, setData] = useState(budgetIntelligenceStore);
  const [filter, setFilter] = useState("all");
  useEffect(() => { budgetIntelligenceStore.fetchOpportunities(); return budgetIntelligenceStore.subscribe(setData); }, []);

  const opps = (data.opportunities || []).filter((o) => filter === "all" || o.opportunity_type === filter);
  const types = [...new Set((data.opportunities || []).map((o) => o.opportunity_type))];
  const totalMonthly = opps.reduce((s, o) => s + (o.monthly_impact || o.potential_savings || 0), 0);
  const totalAnnual = opps.reduce((s, o) => s + (o.annual_impact || 0), 0);

  return (
    <motion.div className="bi-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Savings Opportunities</h1>
        <div className="rec-filters">
          <button className={`btn btn-sm ${filter === "all" ? "btn-primary" : "btn-outline"}`} onClick={() => setFilter("all")}>All ({data.opportunities?.length || 0})</button>
          {types.map((t) => (
            <button key={t} className={`btn btn-sm ${filter === t ? "btn-primary" : "btn-outline"}`} onClick={() => setFilter(t)}>
              {t.replace("_", " ")} ({data.opportunities?.filter((o) => o.opportunity_type === t).length || 0})
            </button>
          ))}
        </div>
      </motion.div>

      {opps.length > 0 && (
        <motion.div className="bi-stats-row" variants={item}>
          <StatWidget label="Opportunities" value={opps.length} change={0} />
          <StatWidget label="Monthly Savings" value={totalMonthly} change={0} prefix="₹" />
          <StatWidget label="Annual Savings" value={totalAnnual} change={0} prefix="₹" />
          <StatWidget label="Avg Confidence" value={opps.length ? (opps.reduce((s, o) => s + (o.confidence_score || 0), 0) / opps.length * 100).toFixed(0) : 0} change={0} suffix="%" />
        </motion.div>
      )}

      {opps.length === 0 && (
        <motion.div className="bi-card" variants={item} style={{ textAlign: "center", color: "#6b7280", padding: 40 }}>
          No savings opportunities found. Run a budget intelligence generation first.
        </motion.div>
      )}

      <div className="bi-opp-grid">
        {opps.map((o) => (
          <motion.div key={o.id} className="bi-opp-card" variants={item}>
            <div className="opp-header">
              <strong>{o.title}</strong>
              <span className="opp-savings">₹{o.potential_savings}/mo</span>
            </div>
            <div style={{ fontSize: "0.72rem", color: "#9ca3af", textTransform: "uppercase", fontWeight: 600 }}>
              {o.opportunity_type?.replace("_", " ")} · {o.category}
            </div>
            <div className="opp-message">{o.message}</div>
            <div style={{ display: "flex", gap: 12, fontSize: "0.8rem" }}>
              <span style={{ color: "#10b981" }}>₹{o.monthly_impact}/mo</span>
              <span style={{ color: "#f59e0b" }}>₹{o.annual_impact}/yr</span>
            </div>
            <div style={{ fontSize: "0.72rem", color: "#6b7280" }}>
              Confidence: {(o.confidence_score * 100).toFixed(0)}%
            </div>
            {o.actionable_steps?.length > 0 && (
              <div style={{ marginTop: 4 }}>
                <div style={{ fontSize: "0.72rem", color: "#9ca3af", marginBottom: 4 }}>Steps:</div>
                <ol style={{ margin: 0, paddingLeft: 16, fontSize: "0.78rem", color: "#d1d5db" }}>
                  {o.actionable_steps.slice(0, 2).map((s, i) => <li key={i}>{s}</li>)}
                </ol>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
