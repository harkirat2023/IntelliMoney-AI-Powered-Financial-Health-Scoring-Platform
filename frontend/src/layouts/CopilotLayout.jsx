import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import "./CopilotLayout.css";

const navItems = [
  { path: "/app/copilot", label: "Chat", end: true },
  { path: "/app/copilot/history", label: "History" },
  { path: "/app/copilot/settings", label: "Settings" },
];

export default function CopilotLayout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="copilot-layout"
    >
      <nav className="copilot-nav">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} end={item.end} className={({ isActive }) => `copilot-nav-link${isActive ? " active" : ""}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="copilot-content">
        <Outlet />
      </div>
    </motion.div>
  );
}
