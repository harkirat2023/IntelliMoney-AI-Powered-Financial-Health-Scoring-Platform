import { useEffect, useState } from "react";
import { AlertCircle, ArrowLeft, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { syncApi } from "../api/sync";
import { bankApi } from "../api/bank";

const STATUS_COLORS = {
  pending: "text-yellow-600 bg-yellow-50",
  running: "text-blue-600 bg-blue-50",
  completed: "text-emerald-600 bg-emerald-50",
  failed: "text-red-600 bg-red-50",
};

export default function SyncHistory() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const filterAccountId = searchParams.get("bank_account_id");

  const [logs, setLogs] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(filterAccountId || "");
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [retrying, setRetrying] = useState(null);
  const [error, setError] = useState(null);
  const limit = 20;

  useEffect(() => {
    bankApi.getAccounts().then((res) => {
      const accts = Array.isArray(res.data) ? res.data : [];
      setAccounts(accts);
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = { limit, offset };
    if (selectedAccount) {
      params.bank_account_id = selectedAccount;
    }
    syncApi
      .history(params)
      .then((res) => {
        const data = res.data;
        setLogs(data.items || []);
        setTotal(data.total || 0);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || "Failed to load sync history");
      })
      .finally(() => setLoading(false));
  }, [selectedAccount, offset]);

  const handleRetry = async (syncLogId) => {
    setRetrying(syncLogId);
    try {
      await syncApi.retry(syncLogId);
      const params = { limit, offset };
      if (selectedAccount) params.bank_account_id = selectedAccount;
      const res = await syncApi.history(params);
      setLogs(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Retry failed");
    } finally {
      setRetrying(null);
    }
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="p-6">
      <button
        onClick={() => navigate("/app/sync")}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft size={16} />
        Back to Sync
      </button>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Sync History</h1>
          <p className="text-gray-500 mt-1">
            View all synchronization attempts
          </p>
        </div>
        <select
          value={selectedAccount}
          onChange={(e) => {
            setSelectedAccount(e.target.value);
            setOffset(0);
          }}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
        >
          <option value="">All Accounts</option>
          {accounts.map((acc) => (
            <option key={acc.id} value={acc.id}>
              {acc.bank_name} ({acc.masked_account_number})
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {loading ? (
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-100 rounded-lg" />
          ))}
        </div>
      ) : logs.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <RefreshCw size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="text-lg font-medium">No sync history yet</p>
          <p className="text-sm mt-1">
            Start your first sync from the Sync page.
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {logs.map((log) => (
              <div
                key={log.id}
                className="bg-white rounded-lg border border-gray-200 p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[log.status] || "text-gray-600 bg-gray-50"}`}
                    >
                      {log.status.charAt(0).toUpperCase() +
                        log.status.slice(1)}
                    </span>
                    <span className="text-sm text-gray-500 capitalize">
                      {log.sync_type}
                    </span>
                    {log.started_at && (
                      <span className="text-sm text-gray-400">
                        {new Date(log.started_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>Fetched: {log.transactions_fetched}</span>
                    <span>Imported: {log.transactions_imported}</span>
                    <span>Skipped: {log.transactions_skipped}</span>
                    {log.status === "failed" && log.retry_count < 3 && (
                      <button
                        onClick={() => handleRetry(log.id)}
                        disabled={retrying === log.id}
                        className="inline-flex items-center gap-1 px-3 py-1 text-sm bg-amber-50 text-amber-700 rounded-lg hover:bg-amber-100 disabled:opacity-50 transition-colors"
                      >
                        <RefreshCw
                          size={14}
                          className={
                            retrying === log.id ? "animate-spin" : ""
                          }
                        />
                        Retry
                      </button>
                    )}
                  </div>
                </div>
                {log.error_message && (
                  <p className="text-xs text-red-500 mt-2">
                    {log.error_message}
                  </p>
                )}
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4 mt-6">
              <button
                onClick={() => setOffset(Math.max(0, offset - limit))}
                disabled={offset === 0}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={16} />
                Previous
              </button>
              <span className="text-sm text-gray-500">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setOffset(offset + limit)}
                disabled={offset + limit >= total}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
