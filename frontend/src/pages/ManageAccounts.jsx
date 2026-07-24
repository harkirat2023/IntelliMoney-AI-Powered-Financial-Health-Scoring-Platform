import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Shield, Loader2, AlertCircle, RefreshCw, Trash2 } from "lucide-react";
import { bankApi } from "../api/bank";
import { BankCard } from "../components/bank/BankCard";
import { DisconnectDialog } from "../components/bank/DisconnectDialog";

export default function ManageAccounts() {
  const location = useLocation();
  const inApp = location.pathname.startsWith("/app");
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
      <div className={`flex items-center justify-center ${inApp ? "page" : "pt-24 pb-16 min-h-screen"}`}>
        <Loader2 size={24} className="animate-spin" style={{ color: "var(--brand-500)" }} />
      </div>
    );
  }

  const content = (
    <div className={inApp ? "page max-w-2xl" : "max-w-2xl mx-auto px-4 sm:px-6 lg:px-8"}>
      <header className="page-header">
        <div>
          <h1>Connected Banks</h1>
          <p>Manage your bank connections</p>
        </div>
        <button onClick={fetchData} className="icon-button" title="Refresh">
          <RefreshCw size={18} />
        </button>
      </header>

      {status && (
        <div className="panel" style={{ background: "var(--brand-50)", borderColor: "var(--brand-200)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <Shield size={20} style={{ color: "var(--brand-600)" }} />
            <div className="muted" style={{ fontSize: "0.9rem" }}>
              <strong style={{ color: "var(--brand-800)" }}>{status.active_accounts} active</strong>
              {" "}connection{status.active_accounts !== 1 ? "s" : ""}
              {status.providers_connected.length > 0 && (
                <> via {status.providers_connected.join(", ")}</>
              )}
            </div>
          </div>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {accounts.length === 0 ? (
        <div className="panel" style={{ textAlign: "center", padding: "40px 20px" }}>
          <Shield size={40} style={{ color: "var(--neutral-300)", marginBottom: "12px" }} />
          <p style={{ fontWeight: 600, color: "var(--neutral-500)", margin: 0 }}>No bank accounts connected</p>
          <p className="muted" style={{ fontSize: "0.85rem", marginTop: "4px" }}>Connect your first bank account to get started.</p>
          <a
            href="/connect-bank"
            className="secondary"
            style={{ display: "inline-flex", alignItems: "center", gap: "6px", marginTop: "16px", padding: "10px 20px", borderRadius: "12px", background: "var(--brand-600)", color: "#fff", fontWeight: 600, fontSize: "0.9rem" }}
          >
            Connect a Bank Account
          </a>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {accounts.map((acc) => (
            <div key={acc.id} style={{ position: "relative" }}>
              <BankCard account={acc} />
              {acc.connection_status === "active" && (
                <button
                  onClick={() => setDisconnecting(acc)}
                  className="icon-button danger"
                  style={{ position: "absolute", top: "8px", right: "8px", opacity: 0.6 }}
                  title="Disconnect"
                >
                  <Trash2 size={14} />
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
  );

  if (inApp) {
    return <div className="page">{content}</div>;
  }

  return (
    <div className="pt-24 pb-16 min-h-screen" style={{ background: "linear-gradient(180deg, var(--neutral-50), #fff)" }}>
      {content}
    </div>
  );
}
