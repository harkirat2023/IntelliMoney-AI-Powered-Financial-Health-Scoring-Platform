import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard, BarChart3, CreditCard, ArrowUpDown, WalletCards, Lightbulb, Bell
} from "lucide-react";
import NotificationCenter from "../dashboard/components/NotificationCenter";
import { dashboardV2Store } from "../store/dashboardV2Store";
import { dashboardV2Api } from "../api/dashboardV2";

const NAV_ITEMS = [
  { to: "/app/dashboard", end: true, icon: LayoutDashboard, label: "Overview" },
  { to: "/app/dashboard/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/app/dashboard/spending", icon: CreditCard, label: "Spending" },
  { to: "/app/dashboard/cashflow", icon: ArrowUpDown, label: "Cash Flow" },
  { to: "/app/dashboard/budgets", icon: WalletCards, label: "Budgets" },
  { to: "/app/dashboard/insights", icon: Lightbulb, label: "Insights" },
];

export default function DashboardLayout() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    dashboardV2Api.getUnreadCount().then((r) => setUnreadCount(r.data.unread_count)).catch(() => {});
    dashboardV2Api.subscribe().catch(() => {});
    const unsub = dashboardV2Store.subscribe((s) => setUnreadCount(s.unreadCount));
    return unsub;
  }, []);

  return (
    <motion.div className="dash-v2-shell" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
      <nav className="dash-v2-nav">
        <div className="dash-nav-brand">
          <LayoutDashboard size={22} />
          <span>Dashboard</span>
        </div>
        <div className="dash-nav-items">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => `dash-nav-item ${isActive ? "active" : ""}`}>
              <item.icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
        <div className="dash-nav-footer">
          <NavLink to="/app/dashboard/notifications" className={({ isActive }) => `dash-nav-item ${isActive ? "active" : ""}`}>
            <Bell size={18} />
            <span>Notifications</span>
            {unreadCount > 0 && <span className="dash-nav-badge">{unreadCount}</span>}
          </NavLink>
        </div>
      </nav>
      <main className="dash-v2-content">
        <div className="dash-topbar">
          <NotificationCenter />
        </div>
        <Outlet />
      </main>
    </motion.div>
  );
}
