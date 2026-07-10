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

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.1 },
  },
};

const itemAnim = {
  hidden: { opacity: 0, x: -10 },
  show: { opacity: 1, x: 0 },
};

export default function DashboardLayout() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    dashboardV2Api.getUnreadCount().then((r) => setUnreadCount(r.data.unread_count)).catch(() => {});
    dashboardV2Api.subscribe().catch(() => {});
    const unsub = dashboardV2Store.subscribe((s) => setUnreadCount(s.unreadCount));
    return unsub;
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="dash-v2-shell"
    >
      <nav className="dash-v2-nav">
        <div className="dash-nav-brand">
          <LayoutDashboard size={22} />
          <span>Dashboard</span>
        </div>
        <motion.div className="dash-nav-items" variants={container} initial="hidden" animate="show">
          {NAV_ITEMS.map((item) => (
            <motion.div key={item.to} variants={itemAnim}>
              <NavLink to={item.to} end={item.end} className={({ isActive }) => `dash-nav-item ${isActive ? "active" : ""}`}>
                <item.icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            </motion.div>
          ))}
        </motion.div>
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
