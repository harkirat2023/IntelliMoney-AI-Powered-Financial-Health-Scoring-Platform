import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { api } from "../api/client";
import { currency } from "../utils/format";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"];

export default function Dashboard() {
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    async function load() {
      try {
        const [summary, monthly, categories, recent, score, recommendations] = await Promise.all([
          api.get("/analytics/summary"),
          api.get("/analytics/monthly-spending"),
          api.get("/analytics/category-breakdown"),
          api.get("/analytics/recent-expenses"),
          api.get("/financial-health/score"),
          api.get("/recommendations")
        ]);
        setState({
          loading: false,
          error: "",
          data: {
            summary: summary.data,
            monthly: monthly.data,
            categories: categories.data,
            recent: recent.data,
            score: score.data,
            recommendations: recommendations.data
          }
        });
      } catch {
        setState({ loading: false, error: "Could not load dashboard data.", data: null });
      }
    }
    load();
  }, []);

  if (state.loading) return <div className="centered">Loading dashboard...</div>;
  if (state.error) return <div className="error">{state.error}</div>;

  const { summary, monthly, categories, recent, score, recommendations } = state.data;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Real-time spending insights and financial health signals.</p>
        </div>
        <div className={`score-pill score-${score.risk_level.toLowerCase().replaceAll(" ", "-")}`}>
          {score.score}/100 · {score.risk_level}
        </div>
      </header>

      <section className="stats-grid">
        <article className="stat"><span>Monthly spending</span><strong>{currency(summary.total_spending)}</strong></article>
        <article className="stat"><span>Income</span><strong>{currency(summary.monthly_income)}</strong></article>
        <article className="stat"><span>Estimated savings</span><strong>{currency(summary.savings_estimate)}</strong></article>
        <article className="stat"><span>Top category</span><strong>{summary.top_category || "None"}</strong></article>
      </section>

      <section className="dashboard-grid">
        <article className="panel wide">
          <h2>Monthly Trend</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip formatter={(value) => currency(value)} />
              <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </article>
        <article className="panel">
          <h2>Category Breakdown</h2>
          {categories.length ? (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={categories} dataKey="value" nameKey="label" innerRadius={55} outerRadius={90}>
                  {categories.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(value) => currency(value)} />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="muted">Add expenses to see category insights.</p>}
        </article>
        <article className="panel">
          <h2>Health Factors</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={[
              { label: "Savings", value: score.savings_rate },
              { label: "Budget", value: score.budget_adherence },
              { label: "Stability", value: score.expense_stability }
            ]}>
              <XAxis dataKey="label" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#16a34a" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel">
          <h2>Recommendations</h2>
          <div className="recommendations">
            {recommendations.map((item, index) => (
              <div className={`recommendation ${item.severity}`} key={index}>
                <strong>{item.title}</strong>
                <p>{item.message}</p>
                <span>{item.suggested_action}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="panel wide">
          <h2>Recent Transactions</h2>
          <div className="table">
            {recent.map((expense) => (
              <div className="table-row" key={expense.id}>
                <span>{expense.description}</span>
                <span>{expense.category}</span>
                <strong>{currency(expense.amount)}</strong>
              </div>
            ))}
            {!recent.length && <p className="muted">No transactions yet.</p>}
          </div>
        </article>
      </section>
    </div>
  );
}
