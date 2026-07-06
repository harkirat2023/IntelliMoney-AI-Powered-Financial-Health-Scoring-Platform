import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Loader2, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { consentApi } from "../api/consent";
import { importPreferenceApi } from "../api/importPreference";
import ReviewSummary from "../components/import/ReviewSummary";

export default function ReviewPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const { account, importType, importStartDate } = location.state || {};
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!user) { navigate("/login", { replace: true }); return; }
    if (!account || !importType) { navigate("/connect-bank/import-preference", { replace: true }); return; }
  }, [user, account, importType, navigate]);

  if (!account || !importType) return null;

  const handleConfirm = async () => {
    setLoading(true);
    setError("");
    try {
      await consentApi.grant({
        bank_account_id: account.id,
        consent_version: "1.0",
        consent_duration_days: 365,
      });
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to save consent. Please try again.";
      setError(msg);
      setLoading(false);
      return;
    }
    try {
      await importPreferenceApi.save({
        bank_account_id: account.id,
        import_type: importType,
        import_start_date: importStartDate || null,
      });
    } catch (err) {
      setError("Import preference could not be saved, but consent was granted. Please try again.");
      setLoading(false);
      return;
    }
    setSuccess(true);
    setTimeout(() => {
      navigate("/connect-bank/complete", {
        state: { account, importType, importStartDate },
      });
    }, 800);
    setLoading(false);
  };

  if (success) {
    return (
      <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <CheckCircle size={28} className="text-emerald-600" />
          </div>
          <p className="text-lg font-semibold text-neutral-900">Preferences Saved!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-emerald-600 transition-colors mb-6"
        >
          <ArrowLeft size={16} />
          Back
        </button>

        <div className="text-center mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">Review & Confirm</h1>
          <p className="mt-2 text-neutral-500 text-sm">
            Please review your selections before confirming.
          </p>
        </div>

        <ReviewSummary
          account={account}
          importType={importType}
          importStartDate={importStartDate}
        />

        <div className="mt-6 p-4 rounded-xl bg-amber-50 border border-amber-100">
          <div className="flex items-start gap-3">
            <AlertCircle size={18} className="text-amber-500 shrink-0 mt-0.5" />
            <div className="text-xs text-amber-800">
              <p className="font-medium">What this means:</p>
              <ul className="mt-1 space-y-0.5 list-disc list-inside">
                <li>IntelliMoney will have read-only access to your transactions</li>
                <li>No funds will be transferred or modified</li>
                <li>You can revoke this consent at any time</li>
                <li>Transaction sync will begin in the next phase</li>
              </ul>
            </div>
          </div>
        </div>

        {error && (
          <div role="alert" className="mt-4 p-3 rounded-xl bg-red-50 border border-red-100 text-sm text-red-700 flex items-center gap-2">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <div className="mt-8">
          <button
            onClick={handleConfirm}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-200/50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Confirming...
              </>
            ) : (
              "Confirm & Complete"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
