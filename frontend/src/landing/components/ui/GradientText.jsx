export function GradientText({
  as: Tag = "span",
  children,
  className = "",
  from = "from-emerald-600",
  to = "to-blue-600",
}) {
  return (
    <Tag className={`bg-gradient-to-r ${from} ${to} bg-clip-text text-transparent ${className}`}>
      {children}
    </Tag>
  );
}
