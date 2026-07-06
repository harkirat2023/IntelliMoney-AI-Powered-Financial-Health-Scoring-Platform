import { useCallback, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { receiptsStore } from "../../store/receiptsStore";
import { receiptsApi } from "../../api/receipts";
import { Loader, CheckCircle, AlertCircle, RefreshCw } from "lucide-react";

const CATEGORIES = [
  "Food & Dining", "Transportation", "Shopping", "Bills & Utilities",
  "Entertainment", "Healthcare", "Education", "Groceries",
  "Rent", "Subscriptions", "Travel", "Other",
];

export default function ReceiptReviewPage() {
  const [searchParams] = useSearchParams();
  const receiptId = searchParams.get("id");
  const [receipt, setReceipt] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    if (receiptId) {
      receiptsStore.fetchReceipt(receiptId).then(() => {
        const r = receiptsStore.currentReceipt;
        setReceipt(r);
        if (r) setForm({ merchant_name: r.merchant_name, total_amount: r.total_amount,
          transaction_date: r.transaction_date, predicted_category: r.predicted_category });
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, [receiptId]);

  const handleProcess = useCallback(async () => {
    if (!receiptId) return;
    setProcessing(true);
    try {
      const res = await receiptsStore.process(receiptId);
      setReceipt(res.receipt);
      setForm({ merchant_name: res.receipt.merchant_name, total_amount: res.receipt.total_amount,
        transaction_date: res.receipt.transaction_date, predicted_category: res.receipt.predicted_category });
      setMessage(res.message);
    } catch (e) {
      setMessage("Processing failed");
    } finally {
      setProcessing(false);
    }
  }, [receiptId]);

  const handleConfirm = useCallback(async () => {
    if (!receiptId) return;
    setConfirming(true);
    try {
      const res = await receiptsStore.confirm(receiptId);
      setReceipt(res.receipt);
      setMessage(`Expense created! ID: ${res.expense_id}`);
    } catch (e) {
      setMessage("Confirmation failed");
    } finally {
      setConfirming(false);
    }
  }, [receiptId]);

  const handleSave = useCallback(async () => {
    if (!receiptId) return;
    setSaving(true);
    try {
      await receiptsStore.updateReceipt(receiptId, form);
      setReceipt(receiptsStore.currentReceipt);
      setEditing(false);
      setMessage("Saved. Process again to recategorize.");
    } catch { }
    finally { setSaving(false); }
  }, [receiptId, form]);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="receipts-page">
      <div className="page-header"><h2><CheckCircle size={20} /> Review Receipt</h2></div>

      {!receiptId ? (
        <div className="empty-state">
          <AlertCircle size={48} />
          <h3>No receipt selected</h3>
          <p>Upload a receipt first, then review it here</p>
          <button className="btn-primary" onClick={() => navigate("/app/receipts/upload")}>Upload</button>
        </div>
      ) : !receipt ? (
        <div className="empty-state">
          <AlertCircle size={48} />
          <h3>Receipt not found</h3>
        </div>
      ) : (
        <div className="review-container">
          <img src={receiptsApi.getImageUrl(receipt.id)} alt="Receipt" className="review-image"
            onError={(e) => { e.target.style.display = "none"; }} />

          <div className="detail-card">
            <h4>Status: <span className={`status-badge ${receipt.status}`}>{receipt.status.replace(/_/g, " ")}</span></h4>
          </div>

          {receipt.status === "uploaded" && (
            <button className="btn-primary" onClick={handleProcess} disabled={processing}>
              {processing ? <Loader className="spin" size={16} /> : <RefreshCw size={16} />} Run OCR
            </button>
          )}

          {message && <p style={{ color: "#f97316", margin: "12px 0" }}>{message}</p>}

          <div className="review-fields">
            <div className="review-row">
              <label>Merchant</label>
              {editing ? (
                <input value={form.merchant_name || ""} onChange={(e) => setForm({ ...form, merchant_name: e.target.value })} />
              ) : (
                <span style={{ color: "#f9fafb", fontWeight: 500 }}>{receipt.merchant_name || "—"}</span>
              )}
            </div>
            <div className="review-row">
              <label>Amount (₹)</label>
              {editing ? (
                <input type="number" value={form.total_amount || 0} onChange={(e) => setForm({ ...form, total_amount: parseFloat(e.target.value) || 0 })} />
              ) : (
                <span style={{ color: "#f97316", fontWeight: 700, fontSize: "1.1rem" }}>₹{receipt.total_amount?.toLocaleString() || "—"}</span>
              )}
            </div>
            <div className="review-row">
              <label>Date</label>
              {editing ? (
                <input type="date" value={form.transaction_date || ""} onChange={(e) => setForm({ ...form, transaction_date: e.target.value })} />
              ) : (
                <span style={{ color: "#f9fafb" }}>{receipt.transaction_date || "—"}</span>
              )}
            </div>
            <div className="review-row">
              <label>Category</label>
              {editing ? (
                <select value={form.predicted_category || ""} onChange={(e) => setForm({ ...form, predicted_category: e.target.value })}>
                  <option value="">Select...</option>
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              ) : (
                <span style={{ color: "#f9fafb" }}>{receipt.predicted_category || "—"} {receipt.confidence_score > 0 && `(${Math.round(receipt.confidence_score * 100)}%)`}</span>
              )}
            </div>
            <div className="review-row">
              <label>Time</label>
              <span style={{ color: "#9ca3af" }}>{receipt.transaction_time || "—"}</span>
            </div>
            <div className="review-row">
              <label>Currency</label>
              <span style={{ color: "#f9fafb" }}>{receipt.currency}</span>
            </div>
          </div>

          <div className="review-actions">
            {receipt.status !== "completed" && (
              <>
                <button className="btn-secondary" onClick={() => { setEditing(!editing); }}>
                  {editing ? "Cancel" : "Edit Fields"}
                </button>
                {editing && (
                  <button className="btn-secondary" onClick={handleSave} disabled={saving}>
                    {saving ? <Loader className="spin" size={16} /> : null} Save
                  </button>
                )}
                <button className="btn-primary" onClick={handleConfirm} disabled={confirming}>
                  {confirming ? <Loader className="spin" size={16} /> : <CheckCircle size={16} />} Confirm & Create Expense
                </button>
              </>
            )}
            {receipt.status === "completed" && (
              <p style={{ color: "#10b981", display: "flex", alignItems: "center", gap: 8 }}>
                <CheckCircle size={16} /> Expense created successfully
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
