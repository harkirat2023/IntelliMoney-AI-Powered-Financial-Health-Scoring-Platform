import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { receiptsStore } from "../../store/receiptsStore";
import { receiptsApi } from "../../api/receipts";
import { Clock, Loader, Trash2 } from "lucide-react";

const STATUS_FILTERS = ["all", "completed", "review_required", "failed"];

export default function ReceiptHistoryPage() {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const navigate = useNavigate();

  useEffect(() => {
    receiptsStore.fetchReceipts().then(() => {
      setReceipts(receiptsStore.receipts);
      setLoading(false);
    });
  }, []);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Delete this receipt?")) return;
    await receiptsStore.deleteReceipt(id);
    setReceipts(receipts.filter((r) => r.id !== id));
  };

  const filtered = filter === "all" ? receipts : receipts.filter((r) => r.status === filter);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  return (
    <div className="receipts-page">
      <div className="page-header">
        <h2><Clock size={20} /> Receipt History</h2>
        <div style={{ display: "flex", gap: 6 }}>
          {STATUS_FILTERS.map((f) => (
            <button key={f} className="btn-secondary"
              style={filter === f ? { borderColor: "#f97316", color: "#f9fafb" } : {}}
              onClick={() => setFilter(f)}>
              {f === "review_required" ? "Needs Review" : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          <Clock size={48} />
          <h3>No receipts found</h3>
        </div>
      ) : (
        <div className="receipt-grid">
          {filtered.map((r) => (
            <div key={r.id} className="receipt-card" onClick={() => navigate(`/app/receipts/review?id=${r.id}`)}>
              {r.image_preview_url && (
                <img src={receiptsApi.getImageUrl(r.id)} alt={r.filename}
                  className="receipt-card-preview" onError={(e) => { e.target.style.display = "none"; }} />
              )}
              <span className={`status-badge ${r.status}`}>{r.status.replace(/_/g, " ")}</span>
              <button className="btn-danger" style={{ position: "absolute", bottom: 12, right: 12, padding: "4px 8px", fontSize: "0.72rem" }}
                onClick={(e) => handleDelete(e, r.id)}>
                <Trash2 size={12} />
              </button>
              <h3>{r.merchant_name || r.filename}</h3>
              {r.total_amount > 0 && <div className="amount">₹{r.total_amount.toLocaleString()}</div>}
              <div className="meta">
                <span>{r.transaction_date || "—"}</span>
                <span>{r.predicted_category || "—"}</span>
              </div>
              <div className="meta" style={{ marginTop: 4 }}>
                <span>OCR: {r.ocr_attempts || 0}x</span>
                <span>{r.expense_id ? "Expense created" : "Pending"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
