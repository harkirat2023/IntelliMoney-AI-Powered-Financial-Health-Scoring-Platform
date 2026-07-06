export default function DateRangePicker({ value, onChange }) {
  const today = new Date().toISOString().split("T")[0];

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-neutral-700">
        Select start date
      </label>
      <input
        type="date"
        value={value || ""}
        max={today}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full px-4 py-2.5 rounded-xl border border-neutral-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 transition-all"
      />
      <p className="text-xs text-neutral-400">
        Transactions on or after this date will be imported.
      </p>
    </div>
  );
}
