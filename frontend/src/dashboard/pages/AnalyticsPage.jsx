import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import StatWidget from "../widgets/StatWidget";
import LineChartCard from "../charts/LineChartCard";
import BarChartCard from "../charts/BarChartCard";
import PieChartCard from "../charts/PieChartCard";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function AnalyticsPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });

  useEffect(() => {
    dashboardV2Store.fetchAnalytics(period);
    const unsub = dashboardV2Store.subscribe(setState);
    return unsub;
  }, [period]);

  const { analytics, loading } = state;
  if (loading && !analytics) return <DashboardSkeleton />;

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.06 } },
  };
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <motion.div className="dash-page" variants={container} initial="hidden" animate="show">
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Analytics</h1>
          <p className="dash-subtitle">Deep dive into your spending patterns</p>
        </div>
        <input type="month" className="dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <motion.div className="dash-stats-grid" variants={item}>
        <StatWidget label="Total Spending" value={analytics?.total_spending || 0} prefix="₹" />
        <StatWidget label="Total Income" value={analytics?.total_income || 0} prefix="₹" />
        <StatWidget label="Net Savings" value={analytics?.net_savings || 0} prefix="₹" />
        <StatWidget label="Avg Daily" value={analytics?.average_daily_spending || 0} prefix="₹" decimals={2} />
      </motion.div>

      <motion.div className="dash-analytics-grid" variants={item}>
        {analytics?.monthly_trend?.length > 0 && (
          <LineChartCard
            title="Income vs Spending"
            data={analytics.monthly_trend}
            lines={[
              { dataKey: "income", color: "#16a34a" },
              { dataKey: "spending", color: "#2563eb" },
              { dataKey: "savings", color: "#7c3aed" },
            ]}
            height={300}
          />
        )}
        {analytics?.spending_by_category?.length > 0 && (
          <BarChartCard
            title="Category Breakdown"
            data={analytics.spending_by_category}
            dataKey="amount"
            height={300}
          />
        )}
        {analytics?.top_merchants?.length > 0 && (
          <BarChartCard
            title="Top Merchants"
            data={analytics.top_merchants}
            dataKey="amount"
            height={300}
          />
        )}
      </motion.div>
    </motion.div>
  );
}
