import { NavLink, Outlet } from "react-router-dom";
import "./HealthLayout.css";

const navItems = [
  { path: "/app/health", label: "Overview", end: true },
  { path: "/app/health/history", label: "History" },
  { path: "/app/health/trends", label: "Trends" },
  { path: "/app/health/recommendations", label: "Recommendations" },
  { path: "/app/health/risk", label: "Risk" },
];

export default function HealthLayout() {
  return (
    <div className="health-layout">
      <nav className="health-nav">
        {navItems.map((item) => (
          <NavLink key={item.path} to={item.path} end={item.end} className={({ isActive }) => `health-nav-link${isActive ? " active" : ""}`}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="health-content">
        <Outlet />
      </div>
    </div>
  );
}
