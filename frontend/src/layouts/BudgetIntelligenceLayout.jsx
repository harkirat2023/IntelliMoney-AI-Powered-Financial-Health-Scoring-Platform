import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import "./BudgetIntelligenceLayout.css";

const navItems = [
  { path: "/app/budget-intelligence", label: "Overview", end: true },
  { path: "/app/budget-intelligence/recommendations", label: "Recommendations" },
  { path: "/app/budget-intelligence/optimization", label: "Optimization" },
  { path: "/app/budget-intelligence/trends", label: "Trends" },
  { path: "/app/budget-intelligence/opportunities", label: "Opportunities" },
];

export default function BudgetIntelligenceLayout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="bi-layout"
    >
      <nav className="bi-nav">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} end={item.end} className={({ isActive }) => `bi-nav-link${isActive ? " active" : ""}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="bi-content">
        <Outlet />
      </div>
    </motion.div>
  );
}
