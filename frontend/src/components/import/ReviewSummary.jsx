import { Building2, Shield, Calendar, Database, Sparkles } from "lucide-react";

const IMPORT_LABELS = {
  import_all: { label: "Import All Transactions", icon: Database },
  start_fresh: { label: "Start Fresh", icon: Sparkles },
  from_date: { label: "Import From Date", icon: Calendar },
};

export default function ReviewSummary({ account, importType, importStartDate }) {
  const importInfo = IMPORT_LABELS[importType] || { label: importType, icon: Database };
  const ImportIcon = importInfo.icon;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-neutral-200">
        <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center shrink-0">
          <Building2 size={22} className="text-emerald-600" />
        </div>
        <div>
          <p className="text-sm text-neutral-500">Connected Bank</p>
          <p className="font-semibold text-neutral-900">{account?.bank_name || "Bank Account"}</p>
          <p className="text-xs text-neutral-400">{account?.masked_account_number || ""}</p>
        </div>
      </div>

      <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-neutral-200">
        <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center shrink-0">
          <Shield size={22} className="text-blue-600" />
        </div>
        <div>
          <p className="text-sm text-neutral-500">Consent Status</p>
          <p className="font-semibold text-neutral-900">Read-only access granted</p>
          <p className="text-xs text-neutral-400">Valid for 1 year • Revocable anytime</p>
        </div>
      </div>

      <div className="flex items-center gap-4 p-4 rounded-xl bg-white border border-neutral-200">
        <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center shrink-0">
          <ImportIcon size={22} className="text-amber-600" />
        </div>
        <div>
          <p className="text-sm text-neutral-500">Import Preference</p>
          <p className="font-semibold text-neutral-900">{importInfo.label}</p>
          {importType === "from_date" && importStartDate && (
            <p className="text-xs text-neutral-400">
              From {new Date(importStartDate).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
