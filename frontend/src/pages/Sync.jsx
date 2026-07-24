import { useEffect, useState, useCallback } from "react";
import {
  AlertCircle, CheckCircle2, Clock, Database, Play, RefreshCw, XCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { syncApi } from "../api/sync";
import { bankApi } from "../api/bank";

const STATUS_ICONS = {
  idle: Clock, running: RefreshCw, completed: CheckCircle2, failed: XCircle, never: AlertCircle,
};

const STATUS_VARIANTS = {
  idle: { bg: "var(--neutral-100)", color: "var(--neutral-600)" },
  running: { bg: "var(--accent-100)", color: "var(--accent-600)" },
  completed: { bg: "var(--brand-100)", color: "var(--brand-700)" },
  failed: { bg: "#fef2f2", color: "#dc2626" },
  never: { bg: "var(--neutral-100)", color: "var(--neutral-400)" },
};

export default function Sync() {
  const navigate = useNavigate();
  const [accounts, setAccounts] = useState([]);
  const [syncStatuses, setSyncStatuses] = useState({});
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const [acctsRes, statusRes] = await Promise.all([
        bankApi.getAccounts(),
        syncApi.status(),
      ]);
      const accts = Array.isArray(acctsRes.data) ? acctsRes.data : [];
      const statuses = Array.isArray(statusRes.data) ? statusRes.data : [];
      setAccounts(accts);
      const statusMap = {};
      statuses.forEach((s) => { statusMap[s.bank_account_id] = s; });
      setSyncStatuses(statusMap);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load sync data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    const hasRunning = Object.values(syncStatuses).some((s) => s.sync_status === "running");
    if (!hasRunning) return;
    const interval = setInterval(() => {
      syncApi.status().then((res) => {
        const statuses = Array.isArray(res.data) ? res.data : [];
        const statusMap = {};
        statuses.forEach((s) => { statusMap[s.bank_account_id] = s; });
        setSyncStatuses(statusMap);
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [syncStatuses]);

  const handleSyncAll = async () => {
    setSyncing(true);
    try {
      await syncApi.manual();
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const handleSyncOne = async (accountId) => {
    try {
      await syncApi.start(accountId);
      await fetchData();
    } catch (err) {
      setError(err.response?.data?.detail || "Sync failed");
    }
  };

  if (loading) {
    return <div className="centered"><RefreshCw size={20} className="spin" /></div>;
  }

  const hasRunning = Object.values(syncStatuses).some((s) => s.sync_status === "running");

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Data Sync</h1>
          <p>Synchronize your bank transactions</p>
        </div>
        <button onClick={handleSyncAll} disabled={syncing || hasRunning || accounts.length === 0}>
          <RefreshCw size={16} className={syncing || hasRunning ? "spin" : ""} />
          {syncing || hasRunning ? "Syncing..." : "Sync All"}
        </button>
      </header>

      {error && <div className="error">{error}</div>}

      {accounts.length === 0 ? (
        <div className="panel" style={{ textAlign: "center", padding: "48px 20px" }}>
          <Database size={48} style={{ color: "var(--neutral-300)", marginBottom: "12px" }} />
          <p style={{ fontWeight: 600, margin: 0 }}>No bank accounts connected</p>
          <p className="muted" style={{ fontSize: "0.85rem", marginTop: "4px" }}>
            Connect a bank account first to start syncing transactions.
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {accounts.map((acc) => {
            const status = syncStatuses[acc.id] || { sync_status: "never", last_synced_at: null, latest_sync: null };
            const StatusIcon = STATUS_ICONS[status.sync_status] || Clock;
            const variant = STATUS_VARIANTS[status.sync_status] || STATUS_VARIANTS.never;
            const isRunning = status.sync_status === "running";

            return (
              <div key={acc.id} className="panel" style={{ padding: "16px 20px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <div style={{ width: 36, height: 36, borderRadius: "8px", background: "var(--brand-50)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Database size={18} style={{ color: "var(--brand-600)" }} />
                    </div>
                    <div>
                      <strong style={{ display: "block" }}>{acc.bank_name}</strong>
                      <span className="muted" style={{ fontSize: "0.82rem" }}>
                        {acc.masked_account_number}
                        {acc.account_type && ` · ${acc.account_type.replace("_", " ")}`}
                      </span>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", padding: "4px 10px", borderRadius: "999px", fontSize: "0.78rem", fontWeight: 600, background: variant.bg, color: variant.color }}>
                      <StatusIcon size={12} className={isRunning ? "spin" : ""} />
                      {status.sync_status === "never" ? "Not Synced" : status.sync_status.charAt(0).toUpperCase() + status.sync_status.slice(1)}
                    </span>
                    <button className="secondary" style={{ minHeight: 32, fontSize: "0.82rem", padding: "0 10px" }} onClick={() => handleSyncOne(acc.id)} disabled={isRunning}>
                      <Play size={12} /> Sync
                    </button>
                    <button className="icon-button" style={{ minHeight: 32, width: 32 }} onClick={() => navigate(`/app/sync/history?bank_account_id=${acc.id}`)} title="History">
                      <Clock size={12} />
                    </button>
                  </div>
                </div>
                {status.last_synced_at && (
                  <p className="muted" style={{ fontSize: "0.78rem", marginTop: "8px", marginBottom: 0 }}>
                    Last synced: {new Date(status.last_synced_at).toLocaleString()}
                    {status.latest_sync?.transactions_imported > 0 && ` · ${status.latest_sync.transactions_imported} transactions imported`}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
