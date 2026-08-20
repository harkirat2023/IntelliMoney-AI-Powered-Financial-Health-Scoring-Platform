import { NavLink, Outlet } from "react-router-dom";

export default function SubNav({ base, items, className = "" }) {
  return (
    <div className={`im-page ${className}`}>
      <div className="im-segmented im-segmented-scroll">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={`${base}${item.path}`}
            end={item.end}
            className={({ isActive }) => `im-segmented-item${isActive ? " active" : ""}`}
          >
            {item.label}
          </NavLink>
        ))}
      </div>
      <Outlet />
    </div>
  );
}