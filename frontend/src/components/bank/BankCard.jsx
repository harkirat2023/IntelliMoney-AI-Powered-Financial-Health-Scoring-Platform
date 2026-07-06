import { Building2, CreditCard, Wallet, Shield, AlertCircle, CheckCircle, Clock } from "lucide-react";

const statusConfig = {
  active: { icon: CheckCircle, color: "text-emerald-600", bg: "bg-emerald-50", label: "Active" },
  expired: { icon: Clock, color: "text-amber-600", bg: "bg-amber-50", label: "Expired" },
  revoked: { icon: AlertCircle, color: "text-red-600", bg: "bg-red-50", label: "Revoked" },
  error: { icon: AlertCircle, color: "text-red-600", bg: "bg-red-50", label: "Error" },
};

const typeIcons = {
  savings: Building2,
  current: Wallet,
  credit_card: CreditCard,
};

export function BankCard({ account }) {
  const StatusIcon = statusConfig[account.connection_status]?.icon || Shield;
  const TypeIcon = typeIcons[account.account_type] || Building2;

  return (
    <div className="flex items-start gap-4 p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-sm transition-shadow">
      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
        <TypeIcon size={18} className="text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-neutral-900 truncate">{account.bank_name}</span>
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${
            statusConfig[account.connection_status]?.bg || "bg-neutral-100"
          } ${statusConfig[account.connection_status]?.color || "text-neutral-600"}`}>
            <StatusIcon size={10} />
            {statusConfig[account.connection_status]?.label || account.connection_status}
          </span>
        </div>
        <p className="text-xs text-neutral-500 mt-0.5">
          {account.masked_account_number} &middot; {account.account_type.replace("_", " ")}
        </p>
        {account.consent_expiry && (
          <p className="text-xs text-neutral-400 mt-1">
            Consent expires: {new Date(account.consent_expiry).toLocaleDateString("en-IN")}
          </p>
        )}
      </div>
    </div>
  );
}
