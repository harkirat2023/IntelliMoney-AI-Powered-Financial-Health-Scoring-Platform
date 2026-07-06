import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Database, Sparkles, Calendar } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import ImportOptionCard from "../components/import/ImportOptionCard";
import EstimatedSummary from "../components/import/EstimatedSummary";
import DateRangePicker from "../components/import/DateRangePicker";

const OPTIONS = [
  {
    key: "import_all",
    icon: Database,
    title: "Import All Transactions",
    description: "Full historical data from this account.",
    estimate: "All available transactions will be imported.",
  },
  {
    key: "start_fresh",
    icon: Sparkles,
    title: "Start Fresh",
    description: "Only future transactions after connection.",
    estimate: "Only new transactions will be synced after account connection.",
  },
  {
    key: "from_date",
    icon: Calendar,
    title: "Import From Specific Date",
    description: "Select a starting date for import.",
  },
];

export default function ImportPreference() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const account = location.state?.account;
  const [selectedType, setSelectedType] = useState(null);
  const [fromDate, setFromDate] = useState("");

  useEffect(() => {
    if (!user) { navigate("/login", { replace: true }); return; }
    if (!account) { navigate("/connect-bank/success", { replace: true }); return; }
  }, [user, account, navigate]);

  if (!account) return null;

  const handleContinue = () => {
    navigate("/connect-bank/review", {
      state: {
        account,
        importType: selectedType,
        importStartDate: selectedType === "from_date" ? fromDate : null,
      },
    });
  };

  const canContinue = selectedType && (selectedType !== "from_date" || fromDate);

  return (
    <div className="pt-24 pb-16 min-h-screen bg-gradient-to-b from-emerald-50/30 via-white to-white">
      <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">
            Set Up Transaction Import
          </h1>
          <p className="mt-2 text-neutral-500 text-sm">
            Choose how much transaction history you'd like to import for{" "}
            <span className="font-medium text-neutral-700">{account.bank_name}</span>.
          </p>
        </div>

        <div className="space-y-3 mb-6">
          {OPTIONS.map((opt) => (
            <ImportOptionCard
              key={opt.key}
              icon={opt.icon}
              title={opt.title}
              description={opt.description}
              estimate={opt.estimate}
              selected={selectedType === opt.key}
              onSelect={() => setSelectedType(opt.key)}
            />
          ))}
        </div>

        {selectedType === "from_date" && (
          <div className="mb-6">
            <DateRangePicker value={fromDate} onChange={setFromDate} />
          </div>
        )}

        <EstimatedSummary importType={selectedType} importStartDate={fromDate} />

        <div className="mt-8">
          <button
            onClick={handleContinue}
            disabled={!canContinue}
            className={`w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all duration-200 ${
              canContinue
                ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-200/50"
                : "bg-neutral-200 text-neutral-400 cursor-not-allowed"
            }`}
          >
            Continue
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
