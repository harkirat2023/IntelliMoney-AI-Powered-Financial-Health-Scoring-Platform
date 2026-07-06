export function SectionHeading({ label, title, description, align = "center" }) {
  const alignClass = align === "center" ? "text-center" : "text-left";

  return (
    <div className={`max-w-2xl mx-auto mb-14 md:mb-16 ${alignClass}`}>
      {label && (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold tracking-wider uppercase text-emerald-700 bg-emerald-100 rounded-full mb-4 border border-emerald-200/50">
          {label}
        </span>
      )}
      {title && (
        <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-neutral-900 tracking-tight leading-[1.1]">
          {title}
        </h2>
      )}
      {description && (
        <p className="mt-5 text-base md:text-lg text-neutral-500 leading-relaxed max-w-xl mx-auto">
          {description}
        </p>
      )}
    </div>
  );
}
