import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../../auth/AuthContext";

import {
  Activity, AlertTriangle, BarChart3, Bot,
  CreditCard, FileText, LayoutDashboard, LogOut, PieChart,
  Receipt, RefreshCw, ShieldCheck, Target,
} from "lucide-react";

const coreItems = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/health", label: "Health Score", icon: Activity },
  { to: "/app/goals", label: "Goals", icon: Target },
  { to: "/app/copilot", label: "AI Copilot", icon: Bot },
];

const integrationsItems = [
  { to: "/app/aa-sandbox", label: "Account Aggregator", icon: ShieldCheck },
];

const toolsItems = [
  { to: "/app/budget-intelligence", label: "Budget Intelligence", icon: PieChart },
  { to: "/app/reports", label: "Reports", icon: FileText },
  { to: "/app/recurring", label: "Recurring", icon: RefreshCw },
  { to: "/app/subscriptions", label: "Subscriptions", icon: CreditCard },
  { to: "/app/anomaly", label: "Anomaly", icon: AlertTriangle },
  { to: "/app/receipts", label: "Receipts", icon: Receipt },
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
        {coreItems.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
        <div className="neon-mono" style={{padding:"16px 14px 8px",fontSize:"0.65rem",letterSpacing:"0.1em",textTransform:"uppercase"}}>
          Integrations
        </div>
        {integrationsItems.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
        <div className="neon-mono" style={{padding:"16px 14px 8px",fontSize:"0.65rem",letterSpacing:"0.1em",textTransform:"uppercase"}}>
          Tools
        </div>
        {toolsItems.map((item) => (
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
