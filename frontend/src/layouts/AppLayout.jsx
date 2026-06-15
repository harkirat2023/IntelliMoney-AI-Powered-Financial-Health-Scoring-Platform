import { BarChart3, CreditCard, Gauge, LogOut, WalletCards } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function AppLayout() {
  const { user, logout } = useAuth();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Gauge size={28} />
          <div>
            <strong>IntelliMoney</strong>
            <span>Financial Health AI</span>
          </div>
        </div>
        <nav>
          <NavLink to="/" end><BarChart3 size={18} /> Dashboard</NavLink>
          <NavLink to="/expenses"><CreditCard size={18} /> Expenses</NavLink>
          <NavLink to="/budgets"><WalletCards size={18} /> Budgets</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span>{user?.name}</span>
          <button className="icon-text" onClick={logout}><LogOut size={16} /> Logout</button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
