import { NavLink, Outlet } from "react-router-dom";
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
    <div className="goals-layout">
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
    </div>
  );
}
