import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import { dashboardV2Api } from "../../api/dashboardV2";
import LineChartCard from "../charts/LineChartCard";
import BarChartCard from "../charts/BarChartCard";
import StatWidget from "../widgets/StatWidget";
import { currency } from "../../utils/format";
import DashboardSkeleton from "../components/DashboardSkeleton";

export default function CashflowPage() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [cashflow, setCashflow] = useState([]);
  const [months, setMonths] = useState(6);

  useEffect(() => {
    const unsub = dashboardV2Store.subscribe(setState);
    dashboardV2Store.fetchOverview();
    dashboardV2Api.getCashflow(months).then((res) => setCashflow(res.data)).catch(() => {});
    return unsub;
  }, [months]);

  const latest = cashflow[0] || {};

  if (!cashflow.length && state.loading) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Cash Flow</h1>
          <p className="dash-subtitle">Track income vs expenses over time</p>
        </div>
        <select className="dash-period-picker" value={months} onChange={(e) => setMonths(Number(e.target.value))}>
          {[3, 6, 12, 24].map((m) => <option key={m} value={m}>{m} months</option>)}
        </select>
      </div>

      <div className="dash-stats-grid">
        <StatWidget label="Total Income" value={latest.total_income || 0} prefix="₹" />
        <StatWidget label="Total Expenses" value={latest.total_expenses || 0} prefix="₹" />
        <StatWidget label="Net Cash Flow" value={latest.net_cash_flow || 0} prefix="₹" />
      </div>

      <div className="dash-overview-grid">
        {cashflow.length > 0 && (
          <LineChartCard
            title="Income vs Expenses"
            data={cashflow.map((c) => ({ month: `${c.month}/${c.year}`, income: c.total_income, expenses: c.total_expenses, net: c.net_cash_flow }))}
            lines={[
              { dataKey: "income", color: "#16a34a" },
              { dataKey: "expenses", color: "#dc2626" },
              { dataKey: "net", color: "#2563eb" },
            ]}
            height={300}
          />
        )}
        {latest.income_by_category?.length > 0 && (
          <BarChartCard title="Income by Category" data={latest.income_by_category} dataKey="amount" height={300} />
        )}
        {latest.expense_by_category?.length > 0 && (
          <BarChartCard title="Expenses by Category" data={latest.expense_by_category} dataKey="amount" height={300} />
        )}
      </div>

      <div className="dash-panel">
        <h3 className="dash-panel-title">Cash Flow History</h3>
        <div className="dash-table">
          {cashflow.map((c, i) => (
            <div className="dash-table-row" key={i}>
              <span>{c.month}/{c.year}</span>
              <span className="text-green">{currency(c.total_income)}</span>
              <span className="text-red">{currency(c.total_expenses)}</span>
              <span className={c.net_cash_flow >= 0 ? "text-green" : "text-red"}>{currency(c.net_cash_flow)}</span>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
