import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import PieChartCard from "../charts/PieChartCard";
import AreaChartCard from "../charts/AreaChartCard";
import BarChartCard from "../charts/BarChartCard";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function SpendingPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });

  useEffect(() => {
    dashboardV2Store.fetchOverview(period);
    dashboardV2Store.fetchWidgets(["spending_heatmap", "top_categories"], period);
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, [period]);

  const { overview, widgets, loading } = state;
  const spending = overview?.spending;

  if (loading && !spending) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Spending</h1>
          <p className="dash-subtitle">Detailed spending analysis</p>
        </div>
        <input type="month" className="dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="dash-stats-grid">
        <div className="dash-widget stat-widget">
          <div className="widget-label">Total Spending</div>
          <div className="dash-stat-value">{currency(spending?.total_spending || 0)}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Transactions</div>
          <div className="dash-stat-value">{spending?.expense_count || 0}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Top Category</div>
          <div className="dash-stat-value">{spending?.top_category || "N/A"}</div>
        </div>
        <div className="dash-widget stat-widget">
          <div className="widget-label">Avg per Transaction</div>
          <div className="dash-stat-value">
            {spending?.expense_count ? currency(spending.total_spending / spending.expense_count) : currency(0)}
          </div>
        </div>
      </div>

      <div className="dash-overview-grid">
        {spending?.spending_by_category?.length > 0 && (
          <PieChartCard title="By Category" data={spending.spending_by_category} height={320} />
        )}
        {overview?.monthly_trend?.length > 0 && (
          <AreaChartCard title="Monthly Trend" data={overview.monthly_trend} dataKey="spending" height={320} />
        )}
        {overview?.top_categories?.length > 0 && (
          <BarChartCard title="Top Categories" data={overview.top_categories} dataKey="amount" height={320} />
        )}
      </div>

      {widgets.spending_heatmap?.length > 0 && (
        <div className="dash-panel">
          <h3 className="dash-panel-title">Spending Activity</h3>
          <div className="heatmap-grid">
            {widgets.spending_heatmap.map((h, i) => (
              <div className="heatmap-cell" key={i} title={`${h.category}: ${currency(h.amount)}`}>
                <div className="heatmap-bar" style={{ height: `${Math.min((h.amount / 10000) * 100, 100)}%` }} />
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
