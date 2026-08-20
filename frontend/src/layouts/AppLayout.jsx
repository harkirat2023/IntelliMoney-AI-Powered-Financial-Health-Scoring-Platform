import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu } from "lucide-react";
import { Outlet, useLocation } from "react-router-dom";

import CyberBackground from "../components/ui/CyberBackground";
import CyberNavRail from "../components/ui/CyberNavRail";
import MobileBottomNav, { MoreSheet } from "../components/ui/MobileBottomNav";
import AlertBell from "../components/AlertBell";
import { useAuth } from "../auth/AuthContext";

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2 } },
};

export default function AppLayout() {
  const location = useLocation();
  const { user } = useAuth();
  const [navOpen, setNavOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);

  return (
    <div className="app-shell">
      <CyberBackground />
      <CyberNavRail open={navOpen} onClose={() => setNavOpen(false)} />
      <main className="cyber-main">
        <div className="cyber-topbar">
          <div className="mobile-brand">
            <button
              className="im-icon-btn mobile-menu-btn"
              onClick={() => setNavOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={20} />
            </button>
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
              <strong>IntelliMoney</strong>
              <span>{user?.name || "Financial Health AI"}</span>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <AlertBell />
          </div>
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
      <MobileBottomNav onMore={() => setMoreOpen(true)} />
      <MoreSheet open={moreOpen} onClose={() => setMoreOpen(false)} />
    </div>
  );
}