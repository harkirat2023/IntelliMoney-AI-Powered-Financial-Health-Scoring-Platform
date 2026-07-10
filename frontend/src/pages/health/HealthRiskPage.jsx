import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { healthStore } from "../../store/healthStore";
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";
import  StatWidget  from "../../dashboard/widgets/StatWidget";
import "./HealthV2.css";

const container = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const item = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } };
const riskColors = { low: "#10b981", moderate: "#f59e0b", high: "#ef4444" };

export default function HealthRiskPage() {
  const [data, setData] = useState(healthStore);
  useEffect(() => { healthStore.fetchRisk(); healthStore.fetchCurrent(); healthStore.fetchBreakdown(); return healthStore.subscribe(setData); }, []);

  const risk = data.risk;
  const dims = risk?.dimensions || [];

  const radarData = dims.map((d) => ({ dimension: d.name, score: d.score }));
  const barData = dims.map((d) => ({ name: d.name, score: d.score, level: d.level }));

  return (
    <motion.div className="health-page" variants={container} initial="hidden" animate="show">
      <motion.div className="page-header" variants={item}>
        <h1>Risk Assessment</h1>
      </motion.div>

      {!risk && (
        <motion.div className="health-card health-empty" variants={item}>
          <p>No risk data available. Run a health calculation first.</p>
        </motion.div>
      )}

      {risk && (
        <>
          <motion.div className="health-stats-row" variants={item}>
            <StatWidget label="Overall Risk" value={risk.overall_risk_level} change={0} />
            <StatWidget label="Risk Score" value={risk.overall_risk_score?.toFixed(1) || "0.0"} change={0} suffix="" />
            <StatWidget label="Health Score" value={data.current?.score || 0} change={0} />
            <StatWidget label="Risk Level" value={100 - (risk.overall_risk_score || 0) >= 80 ? "Low" : 100 - (risk.overall_risk_score || 0) >= 60 ? "Moderate" : "High"} change={0} />
          </motion.div>

          <div className="health-grid-2">
            <motion.div className="health-card" variants={item}>
              <h3>Risk Radar</h3>
              <ResponsiveContainer width="100%" height={320}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#374151" />
                  <PolarAngleAxis dataKey="dimension" tick={{ fill: "#9ca3af", fontSize: 11 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#9ca3af" }} />
                  <Radar name="Risk Score" dataKey="score" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
                </RadarChart>
              </ResponsiveContainer>
            </motion.div>

            <motion.div className="health-card" variants={item}>
              <h3>Risk by Dimension</h3>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={barData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: "#9ca3af", fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" width={90} tick={{ fill: "#9ca3af", fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                    {barData.map((entry, i) => (
                      <Cell key={i} fill={riskColors[entry.level] || "#6b7280"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </motion.div>
          </div>

          <motion.div className="health-card" variants={item}>
            <h3>Dimension Breakdown</h3>
            <div className="dimension-grid">
              {dims.map((d) => (
                <div key={d.name} className="dimension-card" style={{ borderLeft: `4px solid ${riskColors[d.level] || "#6b7280"}` }}>
                  <div className="dim-header">
                    <strong>{d.name}</strong>
                    <span className={`risk-level risk-${d.level}`}>{d.level}</span>
                  </div>
                  <div className="dim-bar-track">
                    <div className="dim-bar-fill" style={{ width: `${d.score}%`, background: riskColors[d.level] || "#6b7280" }} />
                  </div>
                  <span className="dim-score">{d.score}/100</span>
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </motion.div>
  );
}
