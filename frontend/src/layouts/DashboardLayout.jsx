import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutDashboard, BarChart3, CreditCard, ArrowUpDown, WalletCards, Lightbulb, Bell
} from "lucide-react";
import { dashboardV2Store } from "../store/dashboardV2Store";
import { useEffect, useState } from "react";

const SUB_NAV_ITEMS = [
  { to: "/app/dashboard", end: true, icon: LayoutDashboard, label: "Overview" },
  { to: "/app/dashboard/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/app/dashboard/spending", icon: CreditCard, label: "Spending" },
  { to: "/app/dashboard/cashflow", icon: ArrowUpDown, label: "Cash Flow" },
  { to: "/app/dashboard/budgets", icon: WalletCards, label: "Budgets" },
  { to: "/app/dashboard/insights", icon: Lightbulb, label: "Insights" },
  { to: "/app/dashboard/notifications", icon: Bell, label: "Notifications" },
];

export default function DashboardLayout() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsub = dashboardV2Store.subscribe((s) => setUnreadCount(s.unreadCount));
    return unsub;
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      <nav className="dash-sub-nav">
        {SUB_NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) => `dash-sub-link ${isActive ? "active" : ""}`}
          >
            <item.icon size={16} />
            <span>{item.label}</span>
            {item.label === "Notifications" && unreadCount > 0 && (
              <span className="dash-nav-badge">{unreadCount}</span>
            )}
          </NavLink>
        ))}
      </nav>
      <main className="dash-v2-content">
        <Outlet />
      </main>
    </motion.div>
  );
}
