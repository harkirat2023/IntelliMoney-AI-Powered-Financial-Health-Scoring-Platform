import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { healthStore } from "../../store/healthStore";
import  HealthScoreWidget  from "../../dashboard/widgets/HealthScoreWidget";
import  StatWidget  from "../../dashboard/widgets/StatWidget";
import  PieChartCard  from "../../dashboard/charts/PieChartCard";
import  BarChartCard  from "../../dashboard/charts/BarChartCard";
import "./HealthV2.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

export default function HealthOverviewPage() {
  const [data, setData] = useState(healthStore);
  useEffect(() => { healthStore.fetchAll(); return healthStore.subscribe(setData); }, []);

  if (data.loading.current && !data.current) {
    return <div className="health-loading"><div className="health-skeleton" /></div>;
  }

  const factorColors = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#06b6d4", "#84cc16"];

  const pieData = data.breakdown?.factors?.slice(0, 6).map((f, i) => ({
    name: f.name, value: f.contribution || 0, color: factorColors[i % factorColors.length],
  })) || [];

  const barData = data.breakdown?.factors?.map((f, i) => ({
    name: f.name, value: f.value, fill: factorColors[i % factorColors.length],
  })) || [];

  const recs = data.recommendations?.slice(0, 3) || [];

  return (
    <motion.div className="health-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Financial Health</h1>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => healthStore.calculate()} disabled={data.loading.calculate}>
            {data.loading.calculate ? "Calculating..." : "Calculate Now"}
          </button>
          <button className="btn btn-outline" onClick={() => healthStore.recalculate()} disabled={data.loading.calculate}>
            Recalculate
          </button>
        </div>
      </motion.div>

      <motion.div className="health-grid" variants={item}>
        <div className="health-card health-score-card">
          <HealthScoreWidget score={data.current?.score} factors={data.breakdown?.factors} />
        </div>
        <div className="health-card health-stats-grid">
          <StatWidget label="Risk Level" value={data.risk?.overall_risk_level || "N/A"} change={0} />
          <StatWidget label="Volatility" value={data.trends?.volatility?.toFixed(1) || "0.0"} change={0} suffix="%" />
          <StatWidget label="Recommendations" value={data.recommendations?.length || 0} change={0} />
          <StatWidget label="Periods Analyzed" value={data.trends?.periods_analyzed || 0} change={0} />
        </div>
      </motion.div>

      <motion.div className="health-grid-2" variants={item}>
        <div className="health-card">
          <h3>Factor Contribution</h3>
          <PieChartCard data={pieData} title="" />
        </div>
        <div className="health-card">
          <h3>All Factors</h3>
          <BarChartCard data={barData} title="" dataKey="value" />
        </div>
      </motion.div>

      {recs.length > 0 && (
        <motion.div className="health-rec-section" variants={item}>
          <h3>Top Recommendations</h3>
          <div className="rec-strip">
            {recs.map((r) => (
              <div key={r.id} className={`rec-card rec-${r.priority}`}>
                <span className="rec-priority">{r.priority}</span>
                <strong>{r.title}</strong>
                <p>{r.message}</p>
                <div className="rec-metric">
                  <span>{r.metric}: {r.current_value} → {r.target_value}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
