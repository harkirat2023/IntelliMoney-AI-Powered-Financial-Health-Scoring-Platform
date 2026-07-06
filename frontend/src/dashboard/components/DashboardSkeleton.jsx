import { motion } from "framer-motion";

function SkeletonBlock({ width = "100%", height = 20, mb = 12 }) {
  return (
    <motion.div
      className="skeleton-block"
      style={{ width, height, marginBottom: mb, borderRadius: 8 }}
      animate={{ opacity: [0.3, 0.6, 0.3] }}
      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
    />
  );
}

export default function DashboardSkeleton() {
  return (
    <div className="dash-skeleton">
      <div className="skeleton-stats">
        {[1, 2, 3, 4].map((i) => (
          <div className="skeleton-stat" key={i}>
            <SkeletonBlock width="60%" height={14} />
            <SkeletonBlock width="80%" height={28} />
          </div>
        ))}
      </div>
      <div className="skeleton-grid">
        <div className="skeleton-panel"><SkeletonBlock height={200} /></div>
        <div className="skeleton-panel"><SkeletonBlock height={200} /></div>
        <div className="skeleton-panel wide"><SkeletonBlock height={200} /></div>
      </div>
    </div>
  );
}
