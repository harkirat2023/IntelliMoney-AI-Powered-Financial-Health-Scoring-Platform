import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import { dashboardV2Api } from "../../api/dashboardV2";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function BudgetsPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [budgets, setBudgets] = useState(null);
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });

  useEffect(() => {
    dashboardV2Api.getBudgets(period).then((res) => setBudgets(res.data)).catch(() => {});
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, [period]);

  if (!budgets) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Budgets</h1>
          <p className="dash-subtitle">Budget performance for {period}</p>
        </div>
        <input type="month" className="dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="budget-summary-strip">
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.on_track}</span><span className="budget-summary-label safe">On Track</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.warning}</span><span className="budget-summary-label warning">Warning</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.over}</span><span className="budget-summary-label over">Over</span></div>
        <div className="budget-summary-item"><span className="budget-summary-count">{budgets.budgets?.length || 0}</span><span className="budget-summary-label">Total</span></div>
      </div>

      <div className="dash-budget-grid">
        {budgets.budgets?.map((b, i) => {
          const pct = b.percentage_used || 0;
          return (
            <div className={`dash-budget-card ${b.state}`} key={i}>
              <div className="budget-card-header">
                <strong>{b.category}</strong>
                <span className={`budget-state-badge ${b.state}`}>{b.state}</span>
              </div>
              <div className="budget-card-amounts">
                <span>{currency(b.spent)}</span>
                <span className="budget-limit">/ {currency(b.limit)}</span>
              </div>
              <div className="budget-progress-bar">
                <div className="budget-progress-fill" style={{ width: `${Math.min(pct, 100)}%` }} />
              </div>
              <div className="budget-pct">{pct.toFixed(1)}% used</div>
              <div className="budget-remaining">
                {b.state === "over"
                  ? `Over by ${currency(b.spent - b.limit)}`
                  : `${currency(b.limit - b.spent)} remaining`}
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
