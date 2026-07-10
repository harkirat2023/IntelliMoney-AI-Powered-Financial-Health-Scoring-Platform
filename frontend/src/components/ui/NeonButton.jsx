import { motion } from "framer-motion";

export default function NeonButton({
  children,
  variant = "cyan",
  solid = false,
  className = "",
  ...props
}) {
  const base = "neon-btn";
  const variantClass = solid
    ? variant === "pink"
      ? "neon-btn-solid-pink"
      : "neon-btn-solid"
    : variant === "pink"
      ? "neon-btn-pink"
      : "neon-btn-cyan";

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`${base} ${variantClass} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}
