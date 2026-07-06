import { useEffect, useState } from "react";
import { Bell, CheckCheck, X, AlertTriangle, Info, DollarSign, RefreshCw, Database } from "lucide-react";
import { dashboardV2Store } from "../../store/dashboardV2Store";

const ICONS = {
  budget_alert: AlertTriangle,
  processing: RefreshCw,
  sync: Database,
  expense: DollarSign,
  general: Info,
};

export default function NotificationCenter() {
  const [state, setState] = useState(dashboardV2Store.getState());
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const unsub = dashboardV2Store.subscribe(setState);
    dashboardV2Store.fetchNotifications();
    return unsub;
  }, []);

  return (
    <div className="notif-center">
      <button className="notif-bell" onClick={() => { setOpen(!open); dashboardV2Store.fetchNotifications(); }}>
        <Bell size={18} />
        {state.unreadCount > 0 && <span className="notif-count">{state.unreadCount}</span>}
      </button>
      {open && (
        <div className="notif-dropdown">
          <div className="notif-header">
            <strong>Notifications</strong>
            {state.unreadCount > 0 && (
              <button className="notif-mark-all" onClick={() => dashboardV2Store.markAllRead()}>
                <CheckCheck size={14} /> Mark all read
              </button>
            )}
          </div>
          <div className="notif-list">
            {state.notifications.length === 0 && <div className="notif-empty">No notifications</div>}
            {state.notifications.map((n) => {
              const Icon = ICONS[n.type] || Info;
              return (
                <div className={`notif-item ${n.read ? "read" : ""}`} key={n.id} onClick={() => !n.read && dashboardV2Store.markRead(n.id)}>
                  <div className="notif-icon"><Icon size={16} /></div>
                  <div className="notif-content">
                    <strong>{n.title}</strong>
                    <p>{n.message}</p>
                    <small>{new Date(n.created_at).toLocaleDateString()}</small>
                  </div>
                  {!n.read && <span className="notif-dot" />}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
