import { motion } from "framer-motion";
import { useEffect, useState } from "react";

function AnimatedNumber({ value, prefix = "", suffix = "", decimals = 0 }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const num = typeof value === "number" ? value : parseFloat(value) || 0;
    const duration = 800;
    const steps = 30;
    const increment = num / steps;
    let current = 0;
    const interval = setInterval(() => {
      current += increment;
      if (current >= num) {
        setDisplay(num);
        clearInterval(interval);
      } else {
        setDisplay(current);
      }
    }, duration / steps);
    return () => clearInterval(interval);
  }, [value]);

  const format = (n) => {
    if (typeof value === "number" && value > 999) return `${prefix}${(n / 1000).toFixed(1)}k${suffix}`;
    return `${prefix}${n.toFixed(decimals)}${suffix}`;
  };
  return <motion.span className="dash-stat-value" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{format(display)}</motion.span>;
}

export default function StatWidget({ label, value, prefix = "", suffix = "", decimals = 0, icon, change, changeType }) {
  return (
    <article className="dash-widget stat-widget">
      <div className="widget-header">
        {icon && <span className="widget-icon">{icon}</span>}
        <span className="widget-label">{label}</span>
        {change != null && (
          <span className={`change-badge ${changeType || (change >= 0 ? "positive" : "negative")}`}>
            {change >= 0 ? "+" : ""}{change.toFixed(1)}%
          </span>
        )}
      </div>
      <AnimatedNumber value={value} prefix={prefix} suffix={suffix} decimals={decimals} />
    </article>
  );
}
