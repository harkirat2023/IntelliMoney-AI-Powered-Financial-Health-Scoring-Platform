import { NavLink, Outlet } from "react-router-dom";
import "./CopilotLayout.css";

const navItems = [
  { path: "/app/copilot", label: "Chat", end: true },
  { path: "/app/copilot/history", label: "History" },
  { path: "/app/copilot/settings", label: "Settings" },
];

export default function CopilotLayout() {
  return (
    <div className="copilot-layout">
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
    </div>
  );
}
