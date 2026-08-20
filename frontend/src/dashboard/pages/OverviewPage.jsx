import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, PiggyBank, ArrowUpDown, ArrowDownRight, ArrowUpRight } from "lucide-react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import HealthScoreWidget from "../widgets/HealthScoreWidget";
import BudgetStatusWidget from "../widgets/BudgetStatusWidget";
import AreaChartCard from "../charts/AreaChartCard";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";
import { useAuth } from "../../auth/AuthContext";

function SummaryCard({ icon, label, value, change, changeSuffix, tone = "default" }) {
  const positive = change >= 0;
  return (
    <motion.article
      className="im-card stat-widget"
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div className="widget-header">
        <span className="widget-icon">{icon}</span>
        <span className="widget-label">{label}</span>
      </div>
      <div className="im-metric-value">{value}</div>
      {change != null && (
        <div className="im-metric-compare" style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.78rem" }}>
          <span style={{ color: positive ? "var(--ds-ok-strong)" : "var(--ds-danger-strong)", display: "inline-flex", alignItems: "center", gap: 2, fontWeight: 600 }}>
            {positive ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}
            {Math.abs(change)}%
          </span>
          <span style={{ color: "var(--neutral-500)" }}>{changeSuffix || "vs last month"}</span>
        </div>
      )}
    </motion.article>
  );
}

function CategoryBars({ data }) {
  const max = Math.max(...data.map((d) => d.amount), 1);
  return (
    <div className="im-category-bars" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {data.map((item) => (
        <div key={item.category}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 4 }}>
            <span style={{ fontSize: "0.86rem", fontWeight: 600, color: "var(--neutral-700)" }}>{item.category}</span>
            <span style={{ fontSize: "0.86rem", fontWeight: 700, color: "var(--neutral-900)" }}>{currency(item.amount)}</span>
          </div>
          <div className="im-progress">
            <div className="im-progress-fill" style={{ width: `${(item.amount / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function OverviewPage() {
  const { user } = useAuth();
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
  if (error && !overview) {
    return (
      <div className="im-error">
        <span>We couldn't load your financial data.</span>
        <button className="im-btn-primary im-btn" onClick={() => dashboardV2Store.fetchOverview(period)}>Retry</button>
      </div>
    );
  }

  const firstName = (user?.name || "there").split(" ")[0];
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  const spending = overview?.spending || {};
  const income = overview?.income || {};
  const savings = overview?.savings || {};
  const cashFlow = overview?.cash_flow || {};
  const categoryData = spending.spending_by_category || [];

  return (
    <div className="dash-page">
      <div className="im-page-header">
        <div>
          <h1 className="im-page-title">{greeting}, {firstName}</h1>
          <p className="im-page-subtitle">Here's your financial overview for {period}.</p>
        </div>
        <input type="month" className="im-field dash-period-picker" value={period} onChange={(e) => setPeriod(e.target.value)} />
      </div>

      <div className="im-grid im-grid-4">
        <SummaryCard icon={<DollarSign size={16} />} label="Monthly Spending" value={currency(spending.total_spending)} />
        <SummaryCard icon={<TrendingUp size={16} />} label="Monthly Income" value={currency(income.total_income)} />
        <SummaryCard icon={<PiggyBank size={16} />} label="Net Savings" value={currency(savings.net_savings)} change={savings.savings_rate} changeSuffix="savings rate" />
        <SummaryCard icon={<ArrowUpDown size={16} />} label="Cash Flow" value={currency(cashFlow.net_cash_flow)} />
      </div>

      <div className="im-grid im-grid-2">
        <div className="im-card">
          <h3 className="im-h3" style={{ margin: "0 0 16px" }}>Where did your money go?</h3>
          {categoryData.length > 0 ? (
            <CategoryBars data={categoryData} />
          ) : (
            <p className="im-page-subtitle">No spending recorded this period.</p>
          )}
        </div>
        {overview?.monthly_trend?.length > 0 && (
          <AreaChartCard title="Spending Trend" data={overview.monthly_trend} dataKey="spending" color="#10b981" height={280} />
        )}
      </div>

      <div className="im-grid im-grid-2">
        <HealthScoreWidget data={overview?.health_score} />
        <BudgetStatusWidget data={overview?.budget_status} />
      </div>

      {overview?.recent_transactions?.length > 0 && (
        <div className="im-card">
          <h3 className="im-h3" style={{ margin: "0 0 12px" }}>Recent Transactions</h3>
          <div className="dash-tx-list">
            {overview.recent_transactions.slice(0, 8).map((tx) => (
              <div className="dash-tx-item" key={tx.id}>
                <div className="dash-tx-info">
                  <span className="dash-tx-desc">{tx.description || tx.merchant}</span>
                  <span className="dash-tx-cat">{tx.category} · {tx.date}</span>
                </div>
                <span className="dash-tx-amount">−{currency(tx.amount)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}