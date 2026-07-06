import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bell, CheckCheck, AlertTriangle, Info, DollarSign, RefreshCw, Database } from "lucide-react";
import { dashboardV2Store } from "../../store/dashboardV2Store";
import DashboardSkeleton from "../components/DashboardSkeleton";

const ICONS = {
  budget_alert: AlertTriangle,
  processing: RefreshCw,
  sync: Database,
  expense: DollarSign,
  general: Info,
};

export default function NotificationsPage() {
  const [state, setState] = useState(dashboardV2Store.getState());

  useEffect(() => {
    dashboardV2Store.fetchNotifications();
    const unsub = dashboardV2Store.subscribe(setState);
    const interval = setInterval(() => dashboardV2Store.fetchNotifications(), 15000);
    return () => { unsub(); clearInterval(interval); };
  }, []);

  const { notifications, unreadCount, loading } = state;
  if (loading && !notifications.length) return <DashboardSkeleton />;

  return (
    <motion.div className="dash-page" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="dash-page-header">
        <div>
          <h1 className="dash-title">Notifications</h1>
          <p className="dash-subtitle">{unreadCount} unread notifications</p>
        </div>
        {unreadCount > 0 && (
          <button className="dash-btn secondary" onClick={() => dashboardV2Store.markAllRead()}>
            <CheckCheck size={16} /> Mark All Read
          </button>
        )}
      </div>

      <div className="dash-notif-filters">
        <button className="dash-filter-btn active">All</button>
        <button className="dash-filter-btn">Unread</button>
        <button className="dash-filter-btn">Alerts</button>
        <button className="dash-filter-btn">Updates</button>
      </div>

      <div className="dash-notif-list">
        {notifications.length === 0 && (
          <div className="empty-state">
            <Bell size={48} />
            <p>No notifications yet</p>
          </div>
        )}
        {notifications.map((n) => {
          const Icon = ICONS[n.type] || Info;
          return (
            <motion.div
              className={`dash-notif-card ${n.read ? "read" : ""}`}
              key={n.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={() => !n.read && dashboardV2Store.markRead(n.id)}
            >
              <div className="notif-icon-wrap"><Icon size={20} /></div>
              <div className="notif-content-wrap">
                <strong>{n.title}</strong>
                <p>{n.message}</p>
                <small>{new Date(n.created_at).toLocaleString()}</small>
              </div>
              {!n.read && <span className="notif-unread-dot" />}
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
