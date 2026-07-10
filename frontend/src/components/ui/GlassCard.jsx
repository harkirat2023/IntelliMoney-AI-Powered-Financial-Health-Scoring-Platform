import { motion } from "framer-motion";

export default function GlassCard({
  children,
  className = "",
  accent = "cyan",
  hover = true,
  ...props
}) {
  const accentClass = accent === "pink" ? "glass-card-pink" : "glass-card-cyan";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className={`glass-card ${hover ? "hover:border-cyan-500/20" : ""} ${accentClass} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
}
