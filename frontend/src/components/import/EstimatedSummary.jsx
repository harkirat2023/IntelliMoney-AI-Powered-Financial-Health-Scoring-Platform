import { Info } from "lucide-react";

const ESTIMATES = {
  import_all: "All available transactions will be imported.",
  start_fresh: "Only new transactions after account connection.",
  from_date: (date) =>
    date
      ? `Transactions will be imported from ${new Date(date).toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" })}.`
      : "Select a date to estimate the import range.",
};

export default function EstimatedSummary({ importType, importStartDate }) {
  if (!importType) return null;

  const estimateText =
    importType === "from_date"
      ? ESTIMATES.from_date(importStartDate)
      : ESTIMATES[importType];

  return (
    <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-xl border border-emerald-100">
      <div className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0 mt-0.5">
        <Info size={16} className="text-emerald-600" />
      </div>
      <div>
        <p className="text-sm font-medium text-emerald-900 sm:whitespace-normal">
          <span className="sm:hidden">Estimated: </span>
          {estimateText}
        </p>
        <p className="mt-0.5 text-xs text-emerald-600">
          This is an estimate. The actual number may vary.
        </p>
      </div>
    </div>
  );
}
