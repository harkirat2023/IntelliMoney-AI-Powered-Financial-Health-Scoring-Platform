import { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { receiptsStore } from "../../store/receiptsStore";
import { Upload, Camera, FileText, Loader, CheckCircle, AlertCircle } from "lucide-react";

export default function ReceiptUploadPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFile = useCallback((f) => {
    if (!f) return;
    const maxSize = 10 * 1024 * 1024;
    if (f.size > maxSize) {
      setError("File too large. Max 10 MB.");
      return;
    }
    const validTypes = ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"];
    if (!validTypes.includes(f.type) && !f.name.match(/\.(jpg|jpeg|png|bmp|tiff|tif|webp)$/i)) {
      setError("Unsupported file type. Use JPG, PNG, BMP, TIFF, or WebP.");
      return;
    }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setError("");
    setResult(null);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  }, [handleFile]);

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const uploaded = await receiptsStore.upload(file);
      const res = await receiptsStore.process(uploaded.receipt.id);
      setResult(res);
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [file]);

  return (
    <div className="receipts-page">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2><Upload size={20} /> Upload Receipt</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn-secondary" onClick={() => cameraInputRef.current?.click()} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <Camera size={16} /> Take Photo
          </button>
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            hidden
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>
      </div>

      {!result ? (
        <>
          <div className={`upload-zone ${dragging ? "dragging" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}>
            <input ref={inputRef} type="file" accept="image/*" hidden
              onChange={(e) => handleFile(e.target.files[0])} />
            {preview ? (
              <img src={preview} alt="Preview" style={{ maxWidth: "100%", maxHeight: 300, borderRadius: 8 }} />
            ) : (
              <>
                <Upload size={48} style={{ color: "#6b7280" }} />
                <p>Drag & drop a receipt image here, click to browse, or use camera</p>
                <div className="hint">Supports JPG, PNG, BMP, TIFF, WebP &bull; Max 10 MB</div>
              </>
            )}
          </div>

          {error && <p style={{ color: "#ef4444", marginTop: 12, fontSize: "0.85rem" }}><AlertCircle size={14} /> {error}</p>}

          {file && !uploading && (
            <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
              <FileText size={16} style={{ color: "#9ca3af" }} />
              <span style={{ color: "#d1d5db", fontSize: "0.9rem" }}>{file.name}</span>
              <button className="btn-primary" onClick={handleUpload}>
                Upload &amp; Add to Spending
              </button>
            </div>
          )}

          {uploading && (
            <div style={{ marginTop: 16 }}>
              <Loader className="spin" size={20} /> Extracting receipt total and adding to spending...
              <div className="progress-bar"><div className="progress-fill" style={{ width: "60%" }} /></div>
            </div>
          )}
        </>
      ) : (
        <div style={{ textAlign: "center", padding: 40 }}>
          <CheckCircle size={48} style={{ color: "#10b981" }} />
          <h3 style={{ color: "#f9fafb", margin: "16px 0 8px" }}>Receipt Added to Spending!</h3>
          <p style={{ color: "#9ca3af", marginBottom: 20 }}>
            {result.receipt?.merchant_name || "Receipt"} — ₹{result.receipt?.total_amount || "0"} added to your total spending and budget track.
          </p>
          <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
            <button className="btn-primary" onClick={() => navigate(`/app/receipts/review?id=${result.receipt?.id}`)}>
              Review &amp; Edit Details
            </button>
            <button className="btn-secondary" onClick={() => { setFile(null); setPreview(null); setResult(null); }}>
              Upload Another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
