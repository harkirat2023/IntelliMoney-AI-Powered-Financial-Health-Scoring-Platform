import { motion, AnimatePresence } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";

import CyberBackground from "../components/ui/CyberBackground";
import CyberNavRail from "../components/ui/CyberNavRail";
import AlertBell from "../components/AlertBell";

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <CyberBackground />
      <CyberNavRail />
      <main className="cyber-main">
        <div className="cyber-topbar">
          <AlertBell />
        </div>
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
