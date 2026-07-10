import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { healthStore } from "../../store/healthStore";
import  LineChartCard  from "../../dashboard/charts/LineChartCard";
import "./HealthV2.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };

export default function HealthHistoryPage() {
  const [data, setData] = useState(healthStore);
  useEffect(() => { healthStore.fetchHistory(); return healthStore.subscribe(setData); }, []);

  const points = data.history?.history || [];
  const chartData = points.map((p) => ({
    label: p.period,
    Score: p.score,
    "Savings Rate": p.savings_rate,
    "Budget Adherence": p.budget_adherence,
  }));

  return (
    <motion.div className="health-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Health Score History</h1>
      </motion.div>

      <motion.div className="health-card" variants={item}>
        <h3>Score Over Time</h3>
        <LineChartCard data={chartData} title="" lines={["Score", "Savings Rate", "Budget Adherence"]} colors={["#10b981", "#3b82f6", "#f59e0b"]} />
      </motion.div>

      <motion.div className="health-card" variants={item}>
        <h3>All Records</h3>
        <div className="health-table-wrap">
          <table className="health-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Score</th>
                <th>Risk Level</th>
                <th>Savings Rate</th>
                <th>Budget Adherence</th>
                <th>Expense Stability</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p) => (
                <tr key={p.period}>
                  <td>{p.period}</td>
                  <td><span className={`score-badge score-${p.risk_level?.toLowerCase().replace(" ", "-")}`}>{p.score}</span></td>
                  <td>{p.risk_level}</td>
                  <td>{p.savings_rate?.toFixed(1)}%</td>
                  <td>{p.budget_adherence?.toFixed(1)}%</td>
                  <td>{p.expense_stability?.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  );
}
