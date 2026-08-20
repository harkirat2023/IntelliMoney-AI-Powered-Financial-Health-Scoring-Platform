import { NavLink } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";

import {
  Activity, AlertTriangle, BarChart3, Bot,
  CreditCard, FileText, LayoutDashboard, LogOut, PieChart,
  Receipt, RefreshCw, ShieldCheck, Target, X,
} from "lucide-react";

const NAV_GROUPS = [
  {
    label: "Core",
    items: [
      { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard, end: true },
      { to: "/app/health", label: "Health Score", icon: Activity },
      { to: "/app/goals", label: "Goals", icon: Target },
      { to: "/app/copilot", label: "AI Copilot", icon: Bot },
    ],
  },
  {
    label: "Insights",
    items: [
      { to: "/app/budget-intelligence", label: "Budget Intelligence", icon: PieChart },
      { to: "/app/reports", label: "Reports", icon: FileText },
      { to: "/app/anomaly", label: "Anomaly", icon: AlertTriangle },
      { to: "/app/receipts", label: "Receipts", icon: Receipt },
    ],
  },
  {
    label: "Bills",
    items: [
      { to: "/app/recurring", label: "Recurring", icon: RefreshCw },
      { to: "/app/subscriptions", label: "Subscriptions", icon: CreditCard },
    ],
  },
  {
    label: "Integrations",
    items: [
      { to: "/app/aa-sandbox", label: "Account Aggregator", icon: ShieldCheck },
    ],
  },
];

function NavItem({ to, label, icon: Icon, end }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `cyber-nav-link ${isActive ? "active" : ""}`}>
      {Icon && <Icon size={18} />}
      <span>{label}</span>
    </NavLink>
  );
}

export default function CyberNavRail({ open, onClose }) {
  const { user, logout } = useAuth();

  return (
    <>
      {open && <div className="rail-backdrop" onClick={onClose} aria-hidden="true" />}
      <aside className={`cyber-rail${open ? " open" : ""}`}>
        <div className="cyber-rail-brand">
          <div className="cyber-rail-brand-icon">
            <BarChart3 size={20} />
          </div>
          <div className="cyber-rail-brand-text">
            <strong>IntelliMoney</strong>
            <span>Financial Health AI</span>
          </div>
          <button className="im-icon-btn rail-close" onClick={onClose} aria-label="Close menu" style={{ display: "none" }}>
            <X size={18} />
          </button>
        </div>

        <nav className="cyber-rail-nav">
          {NAV_GROUPS.map((group) => (
            <div key={group.label} className="cyber-rail-group-wrap">
              <div className="cyber-rail-group">{group.label}</div>
              {group.items.map((item) => (
                <NavItem key={item.to} {...item} />
              ))}
            </div>
          ))}
        </nav>

        <div className="cyber-rail-footer">
          <span className="cyber-rail-user">{user?.name || "User"}</span>
          <button className="cyber-rail-logout" onClick={logout}>
            <LogOut size={14} /> Logout
          </button>
        </div>
      </aside>
    </>
  );
}