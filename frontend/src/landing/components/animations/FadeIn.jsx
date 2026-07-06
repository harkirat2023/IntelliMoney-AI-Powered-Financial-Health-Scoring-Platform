import { motion } from "framer-motion";
import { useReducedMotion } from "framer-motion";

const directions = {
  up: { y: 40 },
  down: { y: -40 },
  left: { x: 40 },
  right: { x: -40 },
};

const spring = { type: "spring", stiffness: 120, damping: 20 };

export function FadeIn({
  children,
  direction = "up",
  delay = 0,
  duration = 0.5,
  className = "",
  once = true,
  distance = "normal",
}) {
  const reduced = useReducedMotion();
  if (reduced) {
    return <div className={className}>{children}</div>;
  }

  const dist = distance === "far" ? 60 : 40;
  const dir = {
    up: { y: dist },
    down: { y: -dist },
    left: { x: dist },
    right: { x: -dist },
  };

  return (
    <motion.div
      initial={{ opacity: 0, ...dir[direction] }}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once, margin: "-50px" }}
      transition={{ ...spring, duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
