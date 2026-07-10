import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import "./GoalsLayout.css";

const navItems = [
  { path: "/app/goals", label: "Overview", end: true },
  { path: "/app/goals/create", label: "Create Goal" },
  { path: "/app/goals/recommendations", label: "Recommendations" },
  { path: "/app/goals/progress", label: "Progress" },
  { path: "/app/goals/history", label: "History" },
];

export default function GoalsLayout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="goals-layout"
    >
      <nav className="goals-nav">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} end={item.end}
            className={({ isActive }) => `goals-nav-link${isActive ? " active" : ""}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="goals-content">
        <Outlet />
      </div>
    </motion.div>
  );
}
