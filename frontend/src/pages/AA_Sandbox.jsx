import { useCallback, useEffect, useState } from "react";
import {
  CheckCircle2, CloudDownload, Database, FileCheck, Loader2, RefreshCw,
  ShieldAlert, ShieldCheck, XCircle,
} from "lucide-react";

import { aaApi } from "../api/aa";

export default function AASandboxPage() {
  const [mode, setMode] = useState(null);
  const [consents, setConsents] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeConsent, setActiveConsent] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [fetchResult, setFetchResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, consentRes, sessionRes] = await Promise.all([
        aaApi.status(),
        aaApi.listConsents(),
        aaApi.listDataSessions(),
      ]);
      setMode(statusRes.data?.mode || "sandbox");
      setConsents(Array.isArray(consentRes.data) ? consentRes.data : []);
      setSessions(Array.isArray(sessionRes.data) ? sessionRes.data : []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load AA sandbox data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const createConsent = async () => {
    setBusy(true);
    setError("");
    try {
      const res = await aaApi.createConsent("setu");
      setActiveConsent(res.data);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create consent");
    } finally {
      setBusy(false);
    }
  };

  const actOnConsent = async (consentId, action) => {
    setBusy(true);
    setError("");
    try {
      const res = action === "approve" ? await aaApi.approve(consentId) : await aaApi.reject(consentId);
      setActiveConsent(res.data);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${action} consent`);
    } finally {
      setBusy(false);
    }
  };

  const createSession = async (consentId) => {
    setBusy(true);
    setError("");
    try {
      const res = await aaApi.createDataSession(consentId);
      setActiveSession(res.data);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create data session");
    } finally {
      setBusy(false);
    }
  };

  const fetchData = async (sessionId) => {
    setBusy(true);
    setError("");
    try {
      const res = await aaApi.fetchDataSession(sessionId);
      setFetchResult(res.data);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch sandbox data");
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return <div className="centered"><Loader2 size={20} className="spin" /></div>;
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Account Aggregator Sandbox</h1>
          <p>Setu AA demonstration flow — sandbox data only, never production</p>
        </div>
        <button className="secondary" onClick={refresh}><RefreshCw size={16} /> Refresh</button>
      </header>

      <div className="panel" style={{ padding: "14px 18px", background: mode === "sandbox" ? "var(--accent-100)" : "var(--neutral-100)", borderColor: mode === "sandbox" ? "var(--accent-200)" : undefined }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <ShieldAlert size={18} style={{ color: mode === "sandbox" ? "var(--accent-600)" : "var(--neutral-500)" }} />
          <div>
            <strong style={{ fontSize: "0.9rem", display: "block" }}>Mode: {mode === "sandbox" ? "SANDBOX (DEMO)" : String(mode).toUpperCase()}</strong>
            <span className="muted" style={{ fontSize: "0.8rem" }}>
              This flow uses Setu's AA sandbox with simulated data. It is <strong>not</strong> connected to real bank accounts.
            </span>
          </div>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <section className="panel" style={{ padding: "18px 20px", marginTop: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.05rem" }}>1 · Initiate a Consent Request</h2>
            <p className="muted" style={{ fontSize: "0.85rem", margin: "4px 0 0" }}>
              Creates a read-only consent via the Setu AA sandbox provider.
            </p>
          </div>
          <button onClick={createConsent} disabled={busy}>
            {busy ? <><Loader2 size={16} className="spin" /> Creating...</> : <><ShieldCheck size={16} /> Initiate Consent</>}
          </button>
        </div>

        {activeConsent && (
          <ConsentCard
            consent={activeConsent}
            onApprove={() => actOnConsent(activeConsent.id, "approve")}
            onReject={() => actOnConsent(activeConsent.id, "reject")}
            onCreateSession={() => createSession(activeConsent.id)}
            busy={busy}
          />
        )}
      </section>

      {activeSession && (
        <section className="panel" style={{ padding: "18px 20px", marginTop: "16px" }}>
          <h2 style={{ margin: 0, fontSize: "1.05rem" }}>2 · Fetch Sandbox Transactions</h2>
          <p className="muted" style={{ fontSize: "0.85rem", margin: "4px 0 12px" }}>
            Data session <strong>{activeSession.id}</strong> · status{" "}
            <strong>{activeSession.data_status || activeSession.status || "READY"}</strong>
          </p>
          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
            <button onClick={() => fetchData(activeSession.id)} disabled={busy}>
              {busy ? <><Loader2 size={16} className="spin" /> Fetching...</> : <><CloudDownload size={16} /> Fetch Transactions</>}
            </button>
          </div>
          {fetchResult && (
            <div style={{ marginTop: "14px", padding: "12px 14px", borderRadius: "10px", background: "var(--brand-50)" }}>
              <strong style={{ fontSize: "0.9rem" }}>Import complete</strong>
              <ul style={{ margin: "8px 0 0", paddingLeft: "18px", fontSize: "0.85rem" }}>
                <li>Transactions fetched: {fetchResult.transactions_fetched}</li>
                <li>Transactions imported: {fetchResult.transactions_imported}</li>
                <li>Auto-categorized: {fetchResult.categorized ?? "n/a"}</li>
                <li>Financial transactions processed: {fetchResult.processed ?? "n/a"}</li>
              </ul>
            </div>
          )}
        </section>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginTop: "16px" }}>
        <section className="panel" style={{ padding: "18px 20px" }}>
          <h2 style={{ margin: 0, fontSize: "1rem", display: "flex", alignItems: "center", gap: "8px" }}>
            <FileCheck size={16} /> Consents
          </h2>
          {consents.length === 0 ? (
            <p className="muted" style={{ fontSize: "0.85rem" }}>No consents created yet.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
              {consents.map((c) => (
                <div key={c.id} style={{ padding: "10px 12px", borderRadius: "8px", border: "1px solid var(--neutral-200)", fontSize: "0.82rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "8px" }}>
                    <span className="muted">#{c.id.slice(-8)}</span>
                    <StatusPill status={c.consent_status} />
                  </div>
                  <div style={{ display: "flex", gap: "6px", marginTop: "6px", flexWrap: "wrap" }}>
                    {(c.consent_status === "PENDING" || c.consent_status === "REQUESTED") && (
                      <>
                        <button className="secondary" style={{ minHeight: 28, fontSize: "0.75rem", padding: "0 8px" }} onClick={() => actOnConsent(c.id, "approve")} disabled={busy}>Approve</button>
                        <button className="secondary" style={{ minHeight: 28, fontSize: "0.75rem", padding: "0 8px" }} onClick={() => actOnConsent(c.id, "reject")} disabled={busy}>Reject</button>
                      </>
                    )}
                    {(c.consent_status === "APPROVED" || c.consent_status === "ACTIVE") && (
                      <button className="secondary" style={{ minHeight: 28, fontSize: "0.75rem", padding: "0 8px" }} onClick={() => createSession(c.id)} disabled={busy}>
                        <Database size={12} /> Data Session
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="panel" style={{ padding: "18px 20px" }}>
          <h2 style={{ margin: 0, fontSize: "1rem", display: "flex", alignItems: "center", gap: "8px" }}>
            <Database size={16} /> Data Sessions
          </h2>
          {sessions.length === 0 ? (
            <p className="muted" style={{ fontSize: "0.85rem" }}>No data sessions yet.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
              {sessions.map((s) => (
                <div key={s.id} style={{ padding: "10px 12px", borderRadius: "8px", border: "1px solid var(--neutral-200)", fontSize: "0.82rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "8px" }}>
                    <span className="muted">#{s.id.slice(-8)}</span>
                    <StatusPill status={s.data_status || s.status || "READY"} />
                  </div>
                  <button className="secondary" style={{ minHeight: 28, fontSize: "0.75rem", padding: "0 8px", marginTop: "6px" }} onClick={() => fetchData(s.id)} disabled={busy}>
                    <CloudDownload size={12} /> Fetch
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function StatusPill({ status }) {
  const approved = ["APPROVED", "ACTIVE", "READY"].includes(status);
  const rejected = ["REJECTED", "FAILED", "EXPIRED"].includes(status);
  const color = approved ? "var(--brand-700)" : rejected ? "#dc2626" : "var(--accent-600)";
  const bg = approved ? "var(--brand-100)" : rejected ? "#fef2f2" : "var(--accent-100)";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: "4px", padding: "2px 8px", borderRadius: "999px", fontSize: "0.7rem", fontWeight: 600, background: bg, color }}>
      {approved ? <CheckCircle2 size={10} /> : rejected ? <XCircle size={10} /> : <Loader2 size={10} />}
      {status}
    </span>
  );
}

function ConsentCard({ consent, onApprove, onReject, onCreateSession, busy }) {
  return (
    <div style={{ marginTop: "14px", padding: "14px 16px", borderRadius: "10px", border: "1px solid var(--accent-200)", background: "var(--accent-50)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "10px", flexWrap: "wrap" }}>
        <div>
          <strong style={{ fontSize: "0.9rem" }}>{consent.label || "Setu AA Sandbox Consent"}</strong>
          <div className="muted" style={{ fontSize: "0.8rem", marginTop: "2px" }}>
            ID: <code>{consent.id}</code> · handle: <code>{consent.consent_handle}</code>
          </div>
        </div>
        <StatusPill status={consent.consent_status} />
      </div>
      {(consent.consent_status === "PENDING" || consent.consent_status === "REQUESTED") ? (
        <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
          <button onClick={onApprove} disabled={busy}><CheckCircle2 size={14} /> Approve</button>
          <button className="secondary" onClick={onReject} disabled={busy}><XCircle size={14} /> Reject</button>
        </div>
      ) : (
        <div style={{ marginTop: "10px", display: "flex", gap: "8px", alignItems: "center" }}>
          <button onClick={onCreateSession} disabled={busy}><Database size={14} /> Create Data Session</button>
          <span className="muted" style={{ fontSize: "0.8rem" }}>consent approved — proceed to fetch sandbox data</span>
        </div>
      )}
    </div>
  );
}