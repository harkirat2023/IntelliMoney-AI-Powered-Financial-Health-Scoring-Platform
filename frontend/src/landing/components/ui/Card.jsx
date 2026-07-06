const variants = {
  default: "bg-white border border-neutral-200/80 shadow-sm",
  glass: "glass-card",
  highlight: "bg-gradient-to-br from-emerald-50 via-white to-blue-50 border border-emerald-100/80 shadow-md",
  feature: "bg-white border border-neutral-100/80 shadow-sm hover:shadow-lg",
};

export function Card({ variant = "default", hoverable = false, glass = false, children, className = "" }) {
  const base = variants[glass ? "glass" : variant];
  const hover = hoverable ? "transition-all duration-300 hover:-translate-y-1 hover:shadow-lg" : "";
  return (
    <div className={`rounded-2xl p-6 ${base} ${hover} card-glow ${className}`}>
      {children}
    </div>
  );
}
