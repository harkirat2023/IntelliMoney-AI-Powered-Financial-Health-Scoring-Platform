import { useEffect, useState, useCallback } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Database,
  Play,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { syncApi } from "../api/sync";
import { bankApi } from "../api/bank";

const STATUS_ICONS = {
  idle: Clock,
  running: RefreshCw,
  completed: CheckCircle2,
  failed: XCircle,
  never: AlertCircle,
};

const STATUS_COLORS = {
  idle: "text-gray-500",
  running: "text-blue-500 animate-spin",
  completed: "text-emerald-500",
  failed: "text-red-500",
  never: "text-gray-400",
};

const STATUS_BG = {
  idle: "bg-gray-100 text-gray-700",
  running: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  never: "bg-gray-100 text-gray-500",
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
      statuses.forEach((s) => {
        statusMap[s.bank_account_id] = s;
      });
      setSyncStatuses(statusMap);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load sync data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    const hasRunning = Object.values(syncStatuses).some(
      (s) => s.sync_status === "running"
    );
    if (!hasRunning) return;
    const interval = setInterval(() => {
      syncApi.status().then((res) => {
        const statuses = Array.isArray(res.data) ? res.data : [];
        const statusMap = {};
        statuses.forEach((s) => {
          statusMap[s.bank_account_id] = s;
        });
        setSyncStatuses(statusMap);
      });
    }, 5000);
    return () => clearInterval(interval);
  }, [syncStatuses]);

  const handleSyncAll = async () => {
    setSyncing(true);
    try {
      const res = await syncApi.manual();
      const results = res.data?.results || [];
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
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-48" />
          <div className="h-32 bg-gray-200 rounded" />
          <div className="h-32 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  const hasRunning = Object.values(syncStatuses).some(
    (s) => s.sync_status === "running"
  );

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Data Sync</h1>
          <p className="text-gray-500 mt-1">
            Synchronize your bank transactions
          </p>
        </div>
        <button
          onClick={handleSyncAll}
          disabled={syncing || hasRunning || accounts.length === 0}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw size={16} className={syncing || hasRunning ? "animate-spin" : ""} />
          {syncing || hasRunning ? "Syncing..." : "Sync All"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {accounts.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <Database size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">No bank accounts connected</p>
          <p className="text-sm mt-1">
            Connect a bank account first to start syncing transactions.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {accounts.map((acc) => {
            const status = syncStatuses[acc.id] || {
              sync_status: "never",
              last_synced_at: null,
              latest_sync: null,
            };
            const StatusIcon = STATUS_ICONS[status.sync_status] || Clock;
            const spinClass =
              status.sync_status === "running" ? "animate-spin" : "";
            const isRunning = status.sync_status === "running";

            return (
              <div
                key={acc.id}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                      <Database size={20} className="text-emerald-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {acc.bank_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {acc.masked_account_number}
                        {acc.account_type &&
                          ` · ${acc.account_type.replace("_", " ")}`}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_BG[status.sync_status] || STATUS_BG.never}`}
                    >
                      <StatusIcon size={14} className={spinClass} />
                      {status.sync_status === "never"
                        ? "Not Synced"
                        : status.sync_status.charAt(0).toUpperCase() +
                          status.sync_status.slice(1)}
                    </span>
                    <button
                      onClick={() => handleSyncOne(acc.id)}
                      disabled={isRunning}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <Play size={14} />
                      Sync
                    </button>
                    <button
                      onClick={() => navigate(`/app/sync/history?bank_account_id=${acc.id}`)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      History
                    </button>
                  </div>
                </div>
                {status.last_synced_at && (
                  <p className="text-xs text-gray-400 mt-3">
                    Last synced: {new Date(status.last_synced_at).toLocaleString()}
                  </p>
                )}
                {status.latest_sync && status.latest_sync.transactions_imported > 0 && (
                  <p className="text-xs text-gray-400 mt-1">
                    Latest: {status.latest_sync.transactions_imported} transactions imported
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
