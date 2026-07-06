import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, PiggyBank, ArrowUpDown } from "lucide-react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import StatWidget from "../widgets/StatWidget";
import HealthScoreWidget from "../widgets/HealthScoreWidget";
import BudgetStatusWidget from "../widgets/BudgetStatusWidget";
import AreaChartCard from "../charts/AreaChartCard";
import PieChartCard from "../charts/PieChartCard";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function OverviewPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [period, setPeriod] = useState(() => {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  });

  useEffect(() => {
    dashboardV2Store.fetchOverview(period);
    const unsub = dashboardV2Store.subscribe(setState);
    const interval = setInterval(() => dashboardV2Store.fetchOverview(period), 30000);
    return () => { unsub(); clearInterval(interval); };
  }, [period]);

  const { overview, loading, error } = state;

  if (loading && !overview) return <DashboardSkeleton />;
  if (error) return <div className="error">{error}</div>;

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
          <h1 className="dash-title">Overview</h1>
          <p className="dash-subtitle">Your financial snapshot for {period}</p>
        </div>
        <input
          type="month"
          className="dash-period-picker"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
        />
      </div>

      <motion.div className="dash-stats-grid" variants={item}>
        <StatWidget label="Monthly Spending" value={overview?.spending?.total_spending || 0} prefix="₹" icon={<DollarSign size={18} />} />
        <StatWidget label="Monthly Income" value={overview?.income?.total_income || 0} prefix="₹" icon={<TrendingUp size={18} />} />
        <StatWidget label="Net Savings" value={overview?.savings?.net_savings || 0} prefix="₹" change={overview?.savings?.savings_rate} icon={<PiggyBank size={18} />} />
        <StatWidget label="Cash Flow" value={overview?.cash_flow?.net_cash_flow || 0} prefix="₹" icon={<ArrowUpDown size={18} />} />
      </motion.div>

      <motion.div className="dash-overview-grid" variants={item}>
        <HealthScoreWidget data={overview?.health_score} />
        <BudgetStatusWidget data={overview?.budget_status} />
        {overview?.spending?.spending_by_category?.length > 0 && (
          <PieChartCard
            title="Spending by Category"
            data={overview.spending.spending_by_category}
            height={300}
          />
        )}
        {overview?.monthly_trend?.length > 0 && (
          <AreaChartCard
            title="Spending Trend"
            data={overview.monthly_trend}
            dataKey="spending"
            color="#2563eb"
            height={300}
          />
        )}
      </motion.div>

      {overview?.recent_transactions?.length > 0 && (
        <motion.div className="dash-panel" variants={item}>
          <h3 className="dash-panel-title">Recent Transactions</h3>
          <div className="dash-tx-list">
            {overview.recent_transactions.map((tx) => (
              <div className="dash-tx-item" key={tx.id}>
                <div className="dash-tx-info">
                  <span className="dash-tx-desc">{tx.description}</span>
                  <span className="dash-tx-cat">{tx.category}</span>
                </div>
                <span className="dash-tx-amount">{currency(tx.amount)}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
