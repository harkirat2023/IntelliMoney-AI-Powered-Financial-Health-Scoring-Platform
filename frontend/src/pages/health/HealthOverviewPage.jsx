import React, { useEffect, useState } from "react";
import { RefreshCw, Sparkles } from "lucide-react";
import { healthStore } from "../../store/healthStore";
import HealthScoreWidget from "../../dashboard/widgets/HealthScoreWidget";
import PieChartCard from "../../dashboard/charts/PieChartCard";
import BarChartCard from "../../dashboard/charts/BarChartCard";

const factorColors = ["#10b981", "#3b82f6", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#6366f1", "#06b6d4", "#84cc16"];

export default function HealthOverviewPage() {
  const [data, setData] = useState(healthStore);
  useEffect(() => { healthStore.fetchAll(); return healthStore.subscribe(setData); }, []);

  if (data.loading.current && !data.current) {
    return <div className="im-page"><div className="im-skeleton" /></div>;
  }

  const pieData = data.breakdown?.factors?.slice(0, 6).map((f, i) => ({
    name: f.name, value: f.contribution || 0, color: factorColors[i % factorColors.length],
  })) || [];

  const barData = data.breakdown?.factors?.map((f, i) => ({
    name: f.name, value: f.value, fill: factorColors[i % factorColors.length],
  })) || [];

  const recs = data.recommendations?.slice(0, 3) || [];

  return (
    <div className="im-page">
      <div className="im-page-header">
        <div>
          <h1 className="im-page-title">Financial Health</h1>
          <p className="im-page-subtitle">Your overall score and what's driving it.</p>
        </div>
        <div className="im-header-actions">
          <button className="im-btn im-btn-secondary" onClick={() => healthStore.calculate()} disabled={data.loading.calculate}>
            <Sparkles size={14} /> {data.loading.calculate ? "Calculating..." : "Calculate Now"}
          </button>
          <button className="im-btn im-btn-ghost" onClick={() => healthStore.recalculate()} disabled={data.loading.calculate}>
            <RefreshCw size={14} /> Recalculate
          </button>
        </div>
      </div>

      <div className="im-grid im-grid-2">
        <HealthScoreWidget data={data.current} />
        <div className="im-grid im-grid-2">
          <div className="im-card stat-widget">
            <span className="widget-label">Risk Level</span>
            <div className="im-metric-value">{data.risk?.overall_risk_level || "N/A"}</div>
          </div>
          <div className="im-card stat-widget">
            <span className="widget-label">Volatility</span>
            <div className="im-metric-value">{data.trends?.volatility?.toFixed(1) || "0.0"}%</div>
          </div>
          <div className="im-card stat-widget">
            <span className="widget-label">Recommendations</span>
            <div className="im-metric-value">{data.recommendations?.length || 0}</div>
          </div>
          <div className="im-card stat-widget">
            <span className="widget-label">Periods Analyzed</span>
            <div className="im-metric-value">{data.trends?.periods_analyzed || 0}</div>
          </div>
        </div>
      </div>

      <div className="im-grid im-grid-2">
        <div className="im-card">
          <h3 className="im-h3" style={{ margin: "0 0 16px" }}>Factor Contribution</h3>
          <PieChartCard data={pieData} title="" dataKey="value" nameKey="name" />
        </div>
        <div className="im-card">
          <h3 className="im-h3" style={{ margin: "0 0 16px" }}>All Factors</h3>
          <BarChartCard data={barData} title="" dataKey="value" xDataKey="name" />
        </div>
      </div>

      {recs.length > 0 && (
        <div className="im-grid im-grid-3">
          {recs.map((r) => (
            <div className="im-card" key={r.id}>
              <span className={`im-badge ${r.priority === "high" ? "danger" : r.priority === "medium" ? "warning" : "ok"}`}>{r.priority}</span>
              <strong style={{ display: "block", marginTop: 10, color: "var(--neutral-800)" }}>{r.title}</strong>
              <p className="im-page-subtitle" style={{ margin: "6px 0 10px" }}>{r.message}</p>
              <span style={{ fontSize: "0.82rem", color: "var(--neutral-500)" }}>
                {r.metric}: {r.current_value} → {r.target_value}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}