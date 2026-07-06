import { useEffect, useState } from "react";
import { Shield, Loader2, AlertCircle, RefreshCw, Trash2 } from "lucide-react";
import { bankApi } from "../api/bank";
import { BankCard } from "../components/bank/BankCard";
import { DisconnectDialog } from "../components/bank/DisconnectDialog";

export default function ManageAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [disconnecting, setDisconnecting] = useState(null);
  const [disconnectLoading, setDisconnectLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError("");
    try {
      const [accts, stat] = await Promise.all([
        bankApi.getAccounts(),
        bankApi.getStatus(),
      ]);
      setAccounts(accts.data);
      setStatus(stat.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleDisconnect = async () => {
    if (!disconnecting) return;
    setDisconnectLoading(true);
    try {
      await bankApi.disconnect(disconnecting.id);
      setAccounts((prev) => prev.filter((a) => a.id !== disconnecting.id));
      setDisconnecting(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to disconnect");
    } finally {
      setDisconnectLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="pt-24 pb-16 min-h-screen flex items-center justify-center">
        <Loader2 size={24} className="animate-spin text-emerald-600" />
      </div>
    );
  }

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-neutral-50/30 via-white to-white">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">Connected Banks</h1>
            <p className="text-sm text-neutral-500 mt-1">Manage your bank connections</p>
          </div>
          <button
            onClick={fetchData}
            className="p-2 rounded-lg hover:bg-neutral-100 transition-colors"
            title="Refresh"
          >
            <RefreshCw size={18} className="text-neutral-500" />
          </button>
        </div>

        {status && (
          <div className="flex items-center gap-4 p-4 bg-emerald-50 border border-emerald-200 rounded-xl mb-6">
            <Shield size={20} className="text-emerald-600" />
            <div className="text-sm">
              <span className="font-semibold text-emerald-800">{status.active_accounts} active</span>
              <span className="text-emerald-600"> connection{status.active_accounts !== 1 ? "s" : ""}</span>
              {status.providers_connected.length > 0 && (
                <span className="text-emerald-600"> via {status.providers_connected.join(", ")}</span>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 p-4 mb-6 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {accounts.length === 0 ? (
          <div className="text-center py-12 bg-neutral-50 rounded-2xl border border-neutral-200">
            <Shield size={40} className="text-neutral-300 mx-auto mb-3" />
            <p className="text-neutral-500 font-medium">No bank accounts connected</p>
            <p className="text-sm text-neutral-400 mt-1">Connect your first bank account to get started.</p>
            <a
              href="/connect-bank"
              className="inline-flex items-center gap-1 mt-4 px-4 py-2 bg-emerald-600 text-white text-sm font-semibold rounded-xl hover:bg-emerald-700 transition-colors"
            >
              Connect a Bank Account
            </a>
          </div>
        ) : (
          <div className="space-y-3">
            {accounts.map((acc) => (
              <div key={acc.id} className="relative group">
                <BankCard account={acc} />
                {acc.connection_status === "active" && (
                  <button
                    onClick={() => setDisconnecting(acc)}
                    className="absolute top-3 right-3 p-1.5 rounded-lg bg-white border border-neutral-200 opacity-0 group-hover:opacity-100 hover:bg-red-50 hover:border-red-200 transition-all"
                    title="Disconnect"
                  >
                    <Trash2 size={14} className="text-red-500" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}

        {disconnecting && (
          <DisconnectDialog
            account={disconnecting}
            onConfirm={handleDisconnect}
            onCancel={() => setDisconnecting(null)}
            loading={disconnectLoading}
          />
        )}
      </div>
    </div>
  );
}
