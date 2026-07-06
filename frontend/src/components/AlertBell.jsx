import { useEffect, useMemo, useState } from "react";
import { Bell } from "lucide-react";

import { api } from "../api/client";


export default function AlertBell() {
  const [alerts, setAlerts] = useState([]);
  const [open, setOpen] = useState(false);

  async function loadAlerts() {
    const response = await api.get("/alerts");
    setAlerts(response.data);
  }

  useEffect(() => {
    loadAlerts().catch(() => setAlerts([]));
  }, []);

  const unreadCount = useMemo(() => alerts.filter((alert) => !alert.read).length, [alerts]);

  async function markRead(alert) {
    if (!alert.read) {
      const response = await api.patch(`/alerts/${alert.id}/read`);
      setAlerts((current) => current.map((item) => item.id === alert.id ? response.data : item));
    }
  }

  return (
    <div className="alert-bell">
      <button className="icon-button alert-button" onClick={() => setOpen((value) => !value)} aria-label="Budget alerts">
        <Bell size={18} />
        {unreadCount > 0 && <span>{unreadCount}</span>}
      </button>
      {open && (
        <div className="alert-dropdown">
          <div className="alert-dropdown-header">
            <strong>Budget Alerts</strong>
            <small>{unreadCount} unread</small>
          </div>
          <div className="alert-dropdown-list">
            {alerts.map((alert) => (
              <button className={`alert-item ${alert.read ? "read" : ""}`} key={alert.id} onClick={() => markRead(alert)}>
                <span>{alert.message}</span>
                <small>{Math.round(alert.percentage)}% usage</small>
              </button>
            ))}
            {!alerts.length && <p className="muted">No budget alerts yet.</p>}
          </div>
        </div>
      )}
    </div>
  );
}
