import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { budgetIntelligenceStore } from "../../../store/budgetIntelligenceStore";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { StatWidget } from "../../../dashboard/widgets/StatWidget";
import "../../layouts/BudgetIntelligenceLayout.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

const trendColors = { increasing: "#ef4444", decreasing: "#10b981", stable: "#3b82f6" };

export default function BITrendsPage() {
  const [data, setData] = useState(budgetIntelligenceStore);
  useEffect(() => { budgetIntelligenceStore.fetchTrends(); budgetIntelligenceStore.fetchRisk(); return budgetIntelligenceStore.subscribe(setData); }, []);

  const predictions = data.trends?.predictions || [];
  const risk = data.risk;
  const highRiskCount = risk?.high_risk_count || 0;
  const totalCat = (risk?.high_risk_count || 0) + (risk?.medium_risk_count || 0) + (risk?.low_risk_count || 0);

  const chartData = predictions.map((p) => ({
    name: p.category,
    "Predicted": p.predicted_spending,
    "Upper": p.confidence_upper,
    "Lower": p.confidence_lower,
  }));

  return (
    <motion.div className="bi-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Trends & Forecasts</h1>
      </motion.div>

      <motion.div className="bi-stats-row" variants={item}>
        <StatWidget label="Categories Forecasted" value={predictions.length} change={0} />
        <StatWidget label="High Risk Categories" value={highRiskCount} change={0} />
        <StatWidget label="Overall Risk" value={risk?.overall_risk_level || "N/A"} change={0} />
        <StatWidget label="Volatility" value={risk?.volatility_score || 0} change={0} suffix="" />
      </motion.div>

      {chartData.length > 0 && (
        <motion.div className="bi-card" variants={item}>
          <h3>Predicted Spending by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" tick={{ fill: "#9ca3af", fontSize: 11 }} />
              <YAxis tick={{ fill: "#9ca3af" }} />
              <Tooltip />
              <Bar dataKey="Predicted" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => {
                  const pred = predictions[i];
                  const color = pred?.trend_direction ? trendColors[pred.trend_direction] || "#6b7280" : "#6b7280";
                  return <Cell key={i} fill={color} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      <motion.div className="bi-card" variants={item}>
        <h3>Category Predictions</h3>
        <div style={{ overflowX: "auto" }}>
          <table className="bi-trend-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Predicted</th>
                <th>Utilization</th>
                <th>Range</th>
                <th>Trend</th>
                <th>Months</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p) => (
                <tr key={p.category}>
                  <td style={{ fontWeight: 600 }}>{p.category}</td>
                  <td>₹{p.predicted_spending?.toFixed(0)}</td>
                  <td>{p.predicted_utilization?.toFixed(1)}%</td>
                  <td>₹{p.confidence_lower?.toFixed(0)} – ₹{p.confidence_upper?.toFixed(0)}</td>
                  <td><span className={`trend-badge trend-${p.trend_direction}`}>{p.trend_direction}</span></td>
                  <td>{p.months_analyzed}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}
