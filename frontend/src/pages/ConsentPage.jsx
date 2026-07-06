import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Shield, AlertCircle, CheckCircle, Loader2, Eye, XCircle, Info } from "lucide-react";
import { bankApi } from "../api/bank";
import { useAuth } from "../auth/AuthContext";

const consentItems = [
  { icon: Eye, label: "Transaction History", detail: "Read past 12 months of transactions" },
  { icon: Info, label: "Account Details", detail: "Account type, masked number, balance" },
  { icon: Eye, label: "Spending Patterns", detail: "Category-level spending breakdown" },
];

export default function ConsentPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const consentHandle = searchParams.get("consent_handle");
  const provider = searchParams.get("provider");
  const consentToken = searchParams.get("consent_token") || "";
  const state = searchParams.get("state");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  useEffect(() => {
    if (!user) { navigate("/login", { replace: true }); return; }
    if (!consentHandle || !provider) {
      navigate("/connect-bank", { replace: true });
    }
    if (state && user?._id && state !== user._id) {
      setError("Invalid request. Please restart the connection.");
    }
  }, [user, consentHandle, provider, state, navigate]);

  const handleApprove = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await bankApi.submitConsent({
        provider,
        consent_handle: consentHandle,
        consent_token: consentToken,
        account_ids: [],
      });
      navigate("/connect-bank/success", { state: { accounts: res.data } });
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      const detail = err.response?.data?.detail || "";
      if (detail.includes("expired")) {
        setError("Consent has expired. Please restart the connection.");
      } else if (detail.includes("denied")) {
        setError("You denied the consent request.");
      } else {
        setError(detail || "Failed to process consent. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-blue-50/30 via-white to-white">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <Shield size={28} className="text-emerald-600" />
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">Review & Approve</h1>
          <p className="mt-2 text-neutral-500 text-sm">
            {provider === "mock" ? "Mock Bank (Demo)" : provider} is requesting access to:
          </p>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <Info size={18} className="text-amber-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-amber-800">Strictly Read-Only Access</p>
              <ul className="mt-2 space-y-1 text-xs text-amber-700">
                <li className="flex items-center gap-1.5"><CheckCircle size={12} /> View transaction history</li>
                <li className="flex items-center gap-1.5"><XCircle size={12} className="text-red-500" /> No fund transfer capability</li>
                <li className="flex items-center gap-1.5"><XCircle size={12} className="text-red-500" /> No balance modification</li>
                <li className="flex items-center gap-1.5"><XCircle size={12} className="text-red-500" /> No payment processing</li>
                <li className="flex items-center gap-1.5"><CheckCircle size={12} /> You can revoke access anytime</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="space-y-3 mb-8">
          {consentItems.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="flex items-start gap-3 p-4 bg-white border border-neutral-200 rounded-xl">
                <div className="w-9 h-9 rounded-lg bg-emerald-100 flex items-center justify-center flex-shrink-0">
                  <Icon size={16} className="text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-neutral-900">{item.label}</p>
                  <p className="text-xs text-neutral-500">{item.detail}</p>
                </div>
              </div>
            );
          })}
        </div>

        <label className="flex items-start gap-3 mb-6 cursor-pointer">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-0.5 w-4 h-4 rounded border-neutral-300 text-emerald-600 focus:ring-emerald-500"
          />
          <span className="text-sm text-neutral-600">
            I understand that this is read-only access. IntelliMoney will never transfer funds or modify my account balances.
          </span>
        </label>

        {error && (
          <div role="alert" className="flex items-center gap-2 p-4 mb-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <div className="flex flex-col gap-3">
          <button
            onClick={handleApprove}
            disabled={!confirmed || loading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <><Loader2 size={18} className="animate-spin" /> Processing...</>
            ) : (
              <><CheckCircle size={18} /> Approve & Connect</>
            )}
          </button>
          <button
            onClick={() => navigate("/connect-bank")}
            className="w-full px-6 py-3 text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
