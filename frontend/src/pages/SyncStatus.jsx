import { useEffect, useState } from "react";
import {
  AlertCircle,
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Clock,
  Database,
  Play,
  RefreshCw,
  XCircle,
} from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { syncApi } from "../api/sync";

export default function SyncStatus() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const accountId = searchParams.get("account_id");

  const [status, setStatus] = useState(null);
  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const params = accountId ? { bank_account_id: accountId } : {};
      const [statusRes, historyRes] = await Promise.all([
        syncApi.status(accountId),
        syncApi.history({ ...params, limit: 5, offset: 0 }),
      ]);
      const statuses = Array.isArray(statusRes.data) ? statusRes.data : [];
      setStatus(statuses[0] || null);
      setRecentLogs(historyRes.data?.items || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load sync status");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [accountId]);

  useEffect(() => {
    if (!status || status.sync_status !== "running") return;
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [status]);

  const handleSync = async () => {
    if (!accountId) return;
    try {
      await syncApi.start(accountId);
      await fetchStatus();
    } catch (err) {
      setError(err.response?.data?.detail || "Sync failed");
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-48" />
          <div className="h-40 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="p-6">
        <button
          onClick={() => navigate("/app/sync")}
          className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft size={16} />
          Back to Sync
        </button>
        <div className="text-center py-16 text-gray-500">
          <Database size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">Account not found</p>
        </div>
      </div>
    );
  }

  const isRunning = status.sync_status === "running";

  return (
    <div className="p-6">
      <button
        onClick={() => navigate("/app/sync")}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft size={16} />
        Back to Sync
      </button>

      <h1 className="text-2xl font-bold text-gray-900 mb-1">Sync Status</h1>
      <p className="text-gray-500 mb-6">
        {status.bank_name} ({status.masked_account_number})
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <RefreshCw size={16} />
            Sync Status
          </div>
          <div className="flex items-center gap-2">
            {status.sync_status === "completed" && (
              <CheckCircle2 size={20} className="text-emerald-500" />
            )}
            {status.sync_status === "failed" && (
              <XCircle size={20} className="text-red-500" />
            )}
            {status.sync_status === "running" && (
              <RefreshCw size={20} className="text-blue-500 animate-spin" />
            )}
            {status.sync_status === "never" && (
              <Clock size={20} className="text-gray-400" />
            )}
            {status.sync_status === "idle" && (
              <Clock size={20} className="text-gray-400" />
            )}
            <span className="text-lg font-semibold text-gray-900 capitalize">
              {status.sync_status === "never" ? "Not Synced" : status.sync_status}
            </span>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Calendar size={16} />
            Last Synced
          </div>
          <p className="text-lg font-semibold text-gray-900">
            {status.last_synced_at
              ? new Date(status.last_synced_at).toLocaleDateString()
              : "Never"}
          </p>
          {status.last_synced_at && (
            <p className="text-xs text-gray-400 mt-1">
              {new Date(status.last_synced_at).toLocaleTimeString()}
            </p>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
            <Database size={16} />
            Latest Sync
          </div>
          {status.latest_sync ? (
            <>
              <p className="text-lg font-semibold text-gray-900">
                {status.latest_sync.transactions_imported} imported
              </p>
              <p className="text-xs text-gray-400 mt-1 capitalize">
                {status.latest_sync.sync_type} ·{" "}
                {new Date(
                  status.latest_sync.started_at || Date.now()
                ).toLocaleDateString()}
              </p>
            </>
          ) : (
            <p className="text-gray-400">No sync yet</p>
          )}
        </div>
      </div>

      {!isRunning && (
        <button
          onClick={handleSync}
          className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors mb-6"
        >
          <Play size={16} />
          Sync Now
        </button>
      )}

      {isRunning && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm flex items-center gap-2">
          <RefreshCw size={16} className="animate-spin" />
          Sync in progress...
        </div>
      )}

      <h2 className="text-lg font-semibold text-gray-900 mb-3">
        Recent Sync History
      </h2>
      {recentLogs.length === 0 ? (
        <p className="text-gray-400 text-sm">No sync history available.</p>
      ) : (
        <div className="space-y-2">
          {recentLogs.map((log) => (
            <div
              key={log.id}
              className="bg-white rounded-lg border border-gray-200 p-3 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                {log.status === "completed" && (
                  <CheckCircle2 size={16} className="text-emerald-500" />
                )}
                {log.status === "failed" && (
                  <XCircle size={16} className="text-red-500" />
                )}
                {log.status === "running" && (
                  <RefreshCw size={16} className="text-blue-500 animate-spin" />
                )}
                {log.status === "pending" && (
                  <Clock size={16} className="text-yellow-500" />
                )}
                <span className="text-sm text-gray-700 capitalize">
                  {log.sync_type}
                </span>
                <span className="text-sm text-gray-400">
                  {log.started_at
                    ? new Date(log.started_at).toLocaleString()
                    : ""}
                </span>
              </div>
              <span className="text-sm text-gray-500">
                {log.transactions_imported} imported
              </span>
            </div>
          ))}
          <button
            onClick={() =>
              navigate(
                `/app/sync/history${accountId ? `?bank_account_id=${accountId}` : ""}`
              )
            }
            className="text-sm text-emerald-600 hover:text-emerald-700 mt-2"
          >
            View full history →
          </button>
        </div>
      )}
    </div>
  );
}
