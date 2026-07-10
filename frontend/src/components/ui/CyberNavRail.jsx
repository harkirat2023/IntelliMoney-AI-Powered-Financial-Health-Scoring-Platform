import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../../auth/AuthContext";

import {
  Activity, AlertTriangle, BarChart3, Bot, Building2, CreditCard,
  Database, FileText, LayoutDashboard, PieChart, Receipt,
  LogOut, RefreshCw, Settings, Target, WalletCards,
} from "lucide-react";

const iconMap = {
  Activity, AlertTriangle, BarChart3, Bot, Building2,
  CreditCard, Database, FileText, LayoutDashboard, PieChart,
  Receipt, RefreshCw, Settings, Target, WalletCards,
};

const navItems = [
  { to: "/app", label: "Dashboard", icon: BarChart3, end: true },
  { to: "/app/expenses", label: "Expenses", icon: CreditCard },
  { to: "/app/budgets", label: "Budgets", icon: WalletCards },
  { to: "/app/reports", label: "Reports", icon: FileText },
  { to: "/app/recurring", label: "Recurring", icon: RefreshCw },
  { to: "/app/anomaly", label: "Anomaly", icon: AlertTriangle },
  { to: "/app/subscriptions", label: "Subscriptions", icon: RefreshCw },
  { to: "/app/sync", label: "Data Sync", icon: Database },
];

const v2Items = [
  { to: "/app/dashboard", label: "Dashboard V2", icon: LayoutDashboard },
  { to: "/app/health", label: "Health V2", icon: Activity },
  { to: "/app/budget-intelligence", label: "Budget Intel", icon: PieChart },
  { to: "/app/copilot", label: "AI Copilot", icon: Bot },
  { to: "/app/goals", label: "Goals", icon: Target },
  { to: "/app/receipts", label: "Receipts", icon: Receipt },
  { to: "/app/budget-optimizer", label: "Budget Optimizer", icon: Settings },
  { to: "/app/bank-accounts", label: "Bank Accounts", icon: Building2 },
];

function NavItem({ to, label, icon: Icon, end }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `cyber-nav-link ${isActive ? "active" : ""}`}>
      {Icon && <Icon size={16} />}
      <span>{label}</span>
    </NavLink>
  );
}

export default function CyberNavRail() {
  const { user, logout } = useAuth();

  return (
    <motion.aside
      initial={{ x: -240 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="cyber-rail"
    >
      <div className="cyber-rail-brand">
        <div className="cyber-rail-brand-icon">
          <BarChart3 size={20} />
        </div>
        <div className="cyber-rail-brand-text">
          <strong>IntelliMoney</strong>
          <span>Financial Health AI</span>
        </div>
      </div>

      <nav className="cyber-rail-nav">
        <div className="neon-mono" style={{padding:"4px 14px 8px",fontSize:"0.65rem",letterSpacing:"0.1em",textTransform:"uppercase"}}>
          Core
        </div>
        {navItems.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
        <div className="neon-mono" style={{padding:"16px 14px 8px",fontSize:"0.65rem",letterSpacing:"0.1em",textTransform:"uppercase"}}>
          Advanced
        </div>
        {v2Items.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>

      <div className="cyber-rail-footer">
        <span className="cyber-rail-user">{user?.name || "User"}</span>
        <button className="cyber-rail-logout" onClick={logout}>
          <LogOut size={14} /> Logout
        </button>
      </div>
    </motion.aside>
  );
}
