import { useState, useEffect, useCallback } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, BrainCircuit } from "lucide-react";
import { Button } from "../components/ui/Button";
import { navigation } from "../data/navigation";

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const handleEscape = useCallback((e) => {
    if (e.key === "Escape") setOpen(false);
  }, []);

  useEffect(() => {
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [handleEscape]);

  const isActive = (href) => location.pathname === href;

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
      scrolled
        ? "bg-white/85 backdrop-blur-xl border-b border-neutral-200/50 shadow-sm"
        : "bg-transparent"
    }`}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 font-bold text-xl text-neutral-900">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center">
              <BrainCircuit size={20} className="text-white" />
            </div>
            IntelliMoney
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navigation.map((item) => (
              <Link
                key={item.label}
                to={item.href}
                className={`relative px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive(item.href)
                    ? "text-emerald-600 font-semibold"
                    : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100"
                }`}
              >
                {item.label}
                {isActive(item.href) && (
                  <motion.span
                    layoutId="nav-indicator"
                    className="absolute -bottom-0.5 left-2 right-2 h-0.5 bg-emerald-500 rounded-full"
                  />
                )}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" size="sm" href="/login">
              Sign In
            </Button>
            <Button variant="primary" size="sm" href="/register">
              Get Started Free
            </Button>
          </div>

          <button
            className="md:hidden p-2 rounded-lg hover:bg-neutral-100 transition-colors"
            onClick={() => setOpen(!open)}
            aria-expanded={open}
            aria-controls="mobile-menu"
            aria-label={open ? "Close menu" : "Open menu"}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            id="mobile-menu"
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="md:hidden border-t border-neutral-200 bg-white/95 backdrop-blur-xl overflow-hidden shadow-xl"
          >
            <div className="px-4 py-4 space-y-1">
              {navigation.map((item, i) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.05 * i, duration: 0.25 }}
                >
                  <Link
                    to={item.href}
                    onClick={() => setOpen(false)}
                    className={`block px-4 py-2.5 text-sm rounded-xl transition-colors ${
                      isActive(item.href) ? "text-emerald-600 bg-emerald-50 font-semibold" : "text-neutral-600 hover:bg-neutral-50"
                    }`}
                  >
                    {item.label}
                  </Link>
                </motion.div>
              ))}
              <hr className="my-3 border-neutral-100" />
              <div className="space-y-2 pt-1">
                <Button variant="ghost" size="sm" href="/login" className="w-full justify-center">
                  Sign In
                </Button>
                <Button variant="primary" size="sm" href="/register" className="w-full justify-center">
                  Get Started Free
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
