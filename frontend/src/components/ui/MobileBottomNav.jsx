import { NavLink, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity, AlertTriangle, BarChart3, Bot, CreditCard, FileText,
  LayoutDashboard, MoreHorizontal, PieChart, Receipt, RefreshCw,
  ShieldCheck, Target, X,
} from "lucide-react";

const CORE_TABS = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/app/health", label: "Health", icon: Activity },
  { to: "/app/goals", label: "Goals", icon: Target },
  { to: "/app/copilot", label: "Copilot", icon: Bot },
];

const MORE_ITEMS = [
  { to: "/app/budget-intelligence", label: "Budget Intelligence", icon: PieChart },
  { to: "/app/reports", label: "Reports", icon: FileText },
  { to: "/app/anomaly", label: "Anomaly", icon: AlertTriangle },
  { to: "/app/receipts", label: "Receipts", icon: Receipt },
  { to: "/app/recurring", label: "Recurring", icon: RefreshCw },
  { to: "/app/subscriptions", label: "Subscriptions", icon: CreditCard },
  { to: "/app/aa-sandbox", label: "Account Aggregator", icon: ShieldCheck },
];

export default function MobileBottomNav({ onMore }) {
  return (
    <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
      {CORE_TABS.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.end}
          className={({ isActive }) => `mobile-nav-item${isActive ? " active" : ""}`}
        >
          <tab.icon />
          <span>{tab.label}</span>
        </NavLink>
      ))}
      <button className="mobile-nav-item" onClick={onMore} aria-label="More options">
        <MoreHorizontal />
        <span>More</span>
      </button>
    </nav>
  );
}

export function MoreSheet({ open, onClose }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="more-sheet-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="more-sheet"
            initial={{ y: 60 }}
            animate={{ y: 0 }}
            exit={{ y: 60 }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="more-sheet-grabber" />
            <div className="more-sheet-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 className="more-sheet-title" style={{ margin: 0 }}>More</h3>
              <button className="im-icon-btn" onClick={onClose} aria-label="Close menu">
                <X size={18} />
              </button>
            </div>
            <div className="more-sheet-grid">
              {MORE_ITEMS.map((item) => (
                <Link key={item.to} to={item.to} className="more-sheet-item" onClick={onClose}>
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </Link>
              ))}
            </div>
            <p style={{ margin: "16px 0 0", textAlign: "center", fontSize: "0.72rem", color: "var(--neutral-400)" }}>
              <BarChart3 size={12} style={{ verticalAlign: "-2px" }} /> IntelliMoney
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}