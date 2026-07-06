import { Activity, AlertTriangle, BarChart3, Bot, CreditCard, Database, FileText, Gauge, LayoutDashboard, LogOut, PieChart, Receipt, RefreshCw, Settings, Target, WalletCards, Building2 } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import AlertBell from "../components/AlertBell";

export default function AppLayout() {
  const { user, logout } = useAuth();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Gauge size={28} />
          <div>
            <strong>IntelliMoney</strong>
            <span>Financial Health AI</span>
          </div>
        </div>
        <nav>
          <NavLink to="/app" end><BarChart3 size={18} /> Dashboard</NavLink>
          <NavLink to="/app/dashboard"><LayoutDashboard size={18} /> Dashboard V2</NavLink>
          <NavLink to="/app/health"><Activity size={18} /> Health V2</NavLink>
          <NavLink to="/app/budget-intelligence"><PieChart size={18} /> Budget Intel</NavLink>
          <NavLink to="/app/copilot"><Bot size={18} /> AI Copilot</NavLink>
          <NavLink to="/app/goals"><Target size={18} /> Goals</NavLink>
          <NavLink to="/app/receipts"><Receipt size={18} /> Receipts</NavLink>
          <NavLink to="/app/expenses"><CreditCard size={18} /> Expenses</NavLink>
          <NavLink to="/app/budgets"><WalletCards size={18} /> Budgets</NavLink>
          <NavLink to="/app/recurring"><RefreshCw size={18} /> Recurring</NavLink>
          <NavLink to="/app/anomaly"><AlertTriangle size={18} /> Anomaly</NavLink>
          <NavLink to="/app/reports"><FileText size={18} /> Reports</NavLink>
          <NavLink to="/app/subscriptions"><RefreshCw size={18} /> Subscriptions</NavLink>
          <NavLink to="/app/budget-optimizer"><Settings size={18} /> Budget Optimizer</NavLink>
          <NavLink to="/app/bank-accounts"><Building2 size={18} /> Bank Accounts</NavLink>
          <NavLink to="/app/sync"><Database size={18} /> Data Sync</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span>{user?.name}</span>
          <button className="icon-text" onClick={logout}><LogOut size={16} /> Logout</button>
        </div>
      </aside>
      <main className="content">
        <div className="topbar">
          <AlertBell />
        </div>
        <Outlet />
      </main>
    </div>
  );
}
