import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { receiptsStore } from "../../store/receiptsStore";
import { receiptsApi } from "../../api/receipts";
import { Receipt, Plus, Loader, AlertCircle, CheckCircle, Clock } from "lucide-react";

export default function ReceiptsOverviewPage() {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    receiptsStore.fetchReceipts().then(() => {
      setReceipts(receiptsStore.receipts);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading-spinner"><Loader className="spin" /></div>;

  const stats = {
    total: receipts.length,
    completed: receipts.filter((r) => r.status === "completed").length,
    review: receipts.filter((r) => r.status === "review_required").length,
    failed: receipts.filter((r) => r.status === "failed").length,
  };

  return (
    <div className="receipts-page">
      <div className="page-header">
        <h2><Receipt size={20} /> Receipts</h2>
        <button className="btn-primary" onClick={() => navigate("/app/receipts/upload")}>
          <Plus size={16} /> Upload Receipt
        </button>
      </div>

      <div className="receipts-stats">
        <div className="receipt-stat-card">
          <div className="stat-value" style={{ color: "#f97316" }}>{stats.total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="receipt-stat-card">
          <div className="stat-value" style={{ color: "#10b981" }}>{stats.completed}</div>
          <div className="stat-label">Processed</div>
        </div>
        <div className="receipt-stat-card">
          <div className="stat-value" style={{ color: stats.review > 0 ? "#ef4444" : "#6b7280" }}>
            {stats.review}
          </div>
          <div className="stat-label">Needs Review</div>
        </div>
        <div className="receipt-stat-card">
          <div className="stat-value" style={{ color: stats.failed > 0 ? "#ef4444" : "#6b7280" }}>
            {stats.failed}
          </div>
          <div className="stat-label">Failed</div>
        </div>
      </div>

      {receipts.length === 0 ? (
        <div className="empty-state">
          <Receipt size={48} />
          <h3>No receipts yet</h3>
          <p>Upload a receipt image to extract expense data via OCR</p>
          <button className="btn-primary" onClick={() => navigate("/app/receipts/upload")}>
            <Plus size={16} /> Upload
          </button>
        </div>
      ) : (
        <div className="receipt-grid">
          {receipts.map((r) => (
            <div key={r.id} className="receipt-card" onClick={() => navigate(`/app/receipts/${r.id}`)}>
              {r.image_preview_url && (
                <img src={receiptsApi.getImageUrl(r.id)} alt={r.filename}
                  className="receipt-card-preview" onError={(e) => { e.target.style.display = "none"; }} />
              )}
              <span className={`status-badge ${r.status}`}>{r.status.replace(/_/g, " ")}</span>
              <h3>{r.merchant_name || r.filename}</h3>
              {r.total_amount > 0 && <div className="amount">₹{r.total_amount.toLocaleString()}</div>}
              <div className="meta">
                <span>{r.transaction_date || "—"}</span>
                <span>{r.predicted_category || "Uncategorized"}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
