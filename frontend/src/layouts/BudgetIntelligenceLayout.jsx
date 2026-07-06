import { NavLink, Outlet } from "react-router-dom";
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
    <div className="bi-layout">
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
    </div>
  );
}
