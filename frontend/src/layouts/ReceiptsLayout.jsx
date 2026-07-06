import { NavLink, Outlet } from "react-router-dom";
import "./ReceiptsLayout.css";

const navItems = [
  { path: "/app/receipts", label: "Overview", end: true },
  { path: "/app/receipts/upload", label: "Upload" },
  { path: "/app/receipts/review", label: "Review" },
  { path: "/app/receipts/history", label: "History" },
];

export default function ReceiptsLayout() {
  return (
    <div className="receipts-layout">
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
    </div>
  );
}
