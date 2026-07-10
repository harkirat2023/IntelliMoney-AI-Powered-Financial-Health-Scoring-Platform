import { NavLink, Outlet } from "react-router-dom";
import { motion } from "framer-motion";
import "./ReceiptsLayout.css";

const navItems = [
  { path: "/app/receipts", label: "Overview", end: true },
  { path: "/app/receipts/upload", label: "Upload" },
  { path: "/app/receipts/review", label: "Review" },
  { path: "/app/receipts/history", label: "History" },
];

export default function ReceiptsLayout() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="receipts-layout"
    >
      <nav className="receipts-nav">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} end={item.end}
            className={({ isActive }) => `receipts-nav-link${isActive ? " active" : ""}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="receipts-content">
        <Outlet />
      </div>
    </motion.div>
  );
}
