import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { CheckCircle, ArrowRight, Building2, ExternalLink, Loader2 } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { bankApi } from "../api/bank";
import { BankCard } from "../components/bank/BankCard";

export default function CompletePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const { account } = location.state || {};
  const [accounts, setAccounts] = useState(account ? [account] : []);
  const [loading, setLoading] = useState(!account);

  useEffect(() => {
    if (!user) { navigate("/login", { replace: true }); return; }
    if (!accounts.length) {
      bankApi.getAccounts()
        .then((res) => setAccounts(res.data))
        .catch(() => navigate("/connect-bank", { replace: true }))
        .finally(() => setLoading(false));
    }
  }, [user, accounts.length, navigate]);

  if (loading) {
    return (
      <div className="pt-24 pb-16 min-h-screen flex items-center justify-center">
        <Loader2 size={24} className="animate-spin text-emerald-600" />
      </div>
    );
  }

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
          <CheckCircle size={28} className="text-emerald-600" />
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">All Set!</h1>
        <p className="mt-2 text-neutral-500 text-sm max-w-sm mx-auto">
          Your preferences have been saved. We'll notify you when transaction synchronization begins in the next phase.
        </p>

        {accounts.length > 0 && (
          <div className="mt-8 space-y-3 text-left">
            <h3 className="text-sm font-semibold text-neutral-700">Connected Accounts</h3>
            {accounts.map((acc) => (
              <BankCard key={acc.id} account={acc} />
            ))}
          </div>
        )}

        <div className="mt-8 flex flex-col gap-3">
          <button
            onClick={() => navigate("/app")}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors"
          >
            <Building2 size={18} />
            Go to Dashboard
            <ArrowRight size={18} />
          </button>
          <button
            onClick={() => navigate("/connect-bank/manage")}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 text-sm font-medium text-neutral-600 border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-colors"
          >
            <ExternalLink size={16} />
            Manage Accounts
          </button>
        </div>
      </div>
    </div>
  );
}
