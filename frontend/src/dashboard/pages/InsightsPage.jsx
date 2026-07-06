import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Lightbulb, AlertTriangle, Info } from "lucide-react";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function InsightsPage() {
  const [state, setState] = useState(dashboardV2Store.getState());

  useEffect(() => {
    dashboardV2Store.fetchInsights();
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, []);

  const { insights } = state;
  if (!insights) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Insights</h1>
          <p className="dash-subtitle">AI-powered financial insights and alerts</p>
        </div>
      </div>

      {insights.alerts?.length > 0 && (
        <div className="dash-panel">
          <h3 className="dash-panel-title"><AlertTriangle size={18} /> Budget Alerts</h3>
          <div className="dash-insights-list">
            {insights.alerts.map((a, i) => (
              <div className={`dash-insight-card alert ${a.read ? "read" : ""}`} key={i}>
                <div className="insight-icon"><AlertTriangle size={20} /></div>
                <div className="insight-body">
                  <strong>{a.category} — {a.threshold}% threshold</strong>
                  <p>{a.message}</p>
                  <small>Used: {a.percentage.toFixed(1)}%</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {insights.insights?.length > 0 && (
        <div className="dash-panel">
          <h3 className="dash-panel-title"><Lightbulb size={18} /> AI Insights</h3>
          <div className="dash-insights-list">
            {insights.insights.map((ins, i) => (
              <div className={`dash-insight-card ${ins.severity}`} key={i}>
                <div className="insight-icon"><Info size={20} /></div>
                <div className="insight-body">
                  <strong>{ins.title}</strong>
                  <p>{ins.message}</p>
                  <small>{ins.category}</small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!insights.alerts?.length && !insights.insights?.length && (
        <div className="empty-state">
          <Lightbulb size={48} />
          <p>No insights yet. Process some transactions to see AI-powered analysis.</p>
        </div>
      )}
    </motion.div>
  );
}
