const variants = {
  default: "bg-neutral-100 text-neutral-700",
  new: "bg-emerald-100 text-emerald-700",
  accent: "bg-blue-100 text-blue-700",
  premium: "bg-amber-100 text-amber-700",
};

export function Badge({ variant = "default", children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 text-xs font-semibold rounded-full ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
