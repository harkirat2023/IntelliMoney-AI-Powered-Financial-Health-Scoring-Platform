import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Building2, Landmark, CreditCard, ArrowRight, Shield, AlertCircle, Loader2 } from "lucide-react";
import { bankApi } from "../api/bank";
import { useAuth } from "../auth/AuthContext";

const providers = [
  {
    id: "mock",
    name: "Mock Bank (Demo)",
    description: "Test connection with simulated Indian bank accounts. No real data required.",
    icon: Building2,
    banks: "SBI, HDFC, ICICI",
    enabled: true,
  },
  {
    id: "setu",
    name: "Setu",
    description: "Connect via Setu's Account Aggregator platform.",
    icon: Landmark,
    banks: "50+ Indian banks",
    enabled: false,
  },
  {
    id: "finvu",
    name: "Finvu",
    description: "Connect via Finvu's Account Aggregator platform.",
    icon: CreditCard,
    banks: "40+ Indian banks",
    enabled: false,
  },
];

export default function ConnectBank() {
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!authLoading && !user) navigate("/login", { replace: true });
  }, [user, authLoading, navigate]);

  if (authLoading) return null;

  const handleConnect = async () => {
    if (!selected) return;
    setLoading(true);
    setError("");
    try {
      const res = await bankApi.connect(selected.id);
      window.location.href = res.data.consent_url;
    } catch (err) {
      if (err.response?.status === 401) {
        navigate("/login", { replace: true });
        return;
      }
      setError(err.response?.data?.detail || "Failed to connect. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-100 rounded-full text-sm font-medium text-emerald-700 mb-4">
            <Shield size={14} />
            Read-Only Access
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight">
            Connect Your Bank Account
          </h1>
          <p className="mt-3 text-lg text-neutral-500 max-w-lg mx-auto">
            Securely link your bank accounts via RBI-approved Account Aggregators.
            <strong className="text-neutral-700"> We never store your credentials.</strong>
          </p>
        </div>

        <div className="space-y-4 mb-8">
          {providers.map((p) => {
            const Icon = p.icon;
            return (
              <button
                key={p.id}
                onClick={() => p.enabled && setSelected(p)}
                disabled={!p.enabled}
                className={`w-full flex items-start gap-4 p-5 rounded-2xl border-2 text-left transition-all duration-200 ${
                  selected?.id === p.id
                    ? "border-emerald-500 bg-emerald-50 shadow-md"
                    : p.enabled
                    ? "border-neutral-200 bg-white hover:border-emerald-300 hover:shadow-sm"
                    : "border-neutral-100 bg-neutral-50 opacity-50 cursor-not-allowed"
                }`}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  selected?.id === p.id
                    ? "bg-emerald-600 text-white"
                    : "bg-neutral-100 text-neutral-400"
                }`}>
                  <Icon size={22} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-base font-semibold text-neutral-900">{p.name}</span>
                    {!p.enabled && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-neutral-200 text-neutral-500 rounded-full">
                        Coming Soon
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-500 mt-1">{p.description}</p>
                  <p className="text-xs text-neutral-400 mt-1">Supported: {p.banks}</p>
                </div>
              </button>
            );
          })}
        </div>

        {error && (
          <div className="flex items-center gap-2 p-4 mb-6 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        <div className="bg-neutral-50 rounded-2xl border border-neutral-200 p-6 mb-8">
          <h3 className="text-sm font-semibold text-neutral-900 mb-3">What happens when you connect?</h3>
          <ul className="space-y-2 text-sm text-neutral-600">
            {[
              "Read-only access to your transaction history",
              "We categorize your spending automatically",
              "Your bank credentials are never stored",
              "You can revoke access anytime",
              "RBI Account Aggregator framework ensures security",
            ].map((item) => (
              <li key={item} className="flex items-start gap-2">
                <Shield size={14} className="text-emerald-600 mt-0.5 flex-shrink-0" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <button
          onClick={handleConnect}
          disabled={!selected || loading}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <><Loader2 size={18} className="animate-spin" /> Connecting...</>
          ) : (
            <><ArrowRight size={18} /> {selected ? `Connect via ${selected.name}` : "Select a Provider"}
            </>
          )}
        </button>
      </div>
    </div>
  );
}
