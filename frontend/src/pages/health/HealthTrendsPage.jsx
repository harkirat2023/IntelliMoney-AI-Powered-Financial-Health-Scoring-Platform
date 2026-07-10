import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { healthStore } from "../../store/healthStore";
import  AreaChartCard  from "../../dashboard/charts/AreaChartCard";
import  StatWidget  from "../../dashboard/widgets/StatWidget";
import "./HealthV2.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

export default function HealthTrendsPage() {
  const [data, setData] = useState(healthStore);
  useEffect(() => { healthStore.fetchTrends(); healthStore.fetchCurrent(); return healthStore.subscribe(setData); }, []);

  const trend = data.trends;
  const points = trend?.points || [];

  const chartData = points.map((p) => ({
    label: p.period,
    Score: p.score,
    Delta: parseFloat((p.delta || 0).toFixed(1)),
  }));

  const trendLabel = trend?.overall_trend || "—";
  const trendClass = `trend-badge trend-${trendLabel}`;

  return (
    <motion.div className="health-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Trends & Volatility</h1>
      </motion.div>

      <motion.div className="health-stats-row" variants={item}>
        <StatWidget label="Overall Trend" value={trendLabel} change={0} />
        <StatWidget label="Volatility" value={trend?.volatility?.toFixed(2) || "0.00"} change={0} suffix="" />
        <StatWidget label="Periods Analyzed" value={trend?.periods_analyzed || 0} change={0} />
        <StatWidget label="Current Score" value={data.current?.score || 0} change={0} />
      </motion.div>

      <motion.div className="health-card" variants={item}>
        <h3>Score Trend <span className={trendClass}>{trendLabel}</span></h3>
        <AreaChartCard data={chartData} title="" dataKey="Score" color="#10b981" />
      </motion.div>

      <motion.div className="health-card" variants={item}>
        <h3>Period-over-Period Delta</h3>
        <AreaChartCard data={chartData} title="" dataKey="Delta" color="#f59e0b" />
      </motion.div>
    </motion.div>
  );
}
