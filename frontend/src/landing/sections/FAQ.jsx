import { useState } from "react";
import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";
import { faqItems as faq } from "../data/faq";
import { ChevronDown, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function AccordionItem({ item, index }) {
  const [open, setOpen] = useState(false);
  const panelId = `faq-panel-${index}`;
  const buttonId = `faq-button-${index}`;

  return (
    <div className={`border rounded-xl overflow-hidden transition-all duration-300 ${open ? "border-emerald-200 bg-emerald-50/30 shadow-sm" : "border-neutral-200 hover:border-neutral-300"}`}>
      <button
        id={buttonId}
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-controls={panelId}
        className="w-full flex items-center justify-between px-5 py-4 text-left bg-transparent transition-colors focus-visible:ring-2 focus-visible:ring-emerald-500/50 focus-visible:outline-none focus-visible:ring-inset"
      >
        <span className="text-sm font-medium text-neutral-900 pr-4">{item.question}</span>
        <ChevronDown
          size={16}
          className={`text-neutral-400 flex-shrink-0 transition-all duration-300 ${open ? "rotate-180 text-emerald-500" : ""}`}
        />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={panelId}
            role="region"
            aria-labelledby={buttonId}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 24 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4 text-sm text-neutral-500 leading-relaxed bg-white">
              {item.answer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function FAQ() {
  const [search, setSearch] = useState("");
  const filtered = faq.filter(
    (item) =>
      item.question.toLowerCase().includes(search.toLowerCase()) ||
      item.answer.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <section id="faq" className="py-16 md:py-24 bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="FAQ"
          title="Got Questions?"
          description="Everything you need to know about IntelliMoney."
        />

        <FadeIn>
          <div className="relative mb-8">
            <input
              type="text"
              aria-label="Search frequently asked questions"
              placeholder="Search questions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-3 pl-10 pr-10 text-sm bg-neutral-50 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-colors"
            />
            <svg aria-hidden="true" className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {search && (
              <button
                onClick={() => setSearch("")}
                aria-label="Clear search"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </FadeIn>

        {filtered.length > 0 && (
          <p className="text-xs text-neutral-400 mb-4">{filtered.length} result{filtered.length !== 1 ? "s" : ""}</p>
        )}

        <div className="space-y-3">
          {filtered.map((item, i) => (
            <FadeIn key={i} delay={i * 0.05}>
              <AccordionItem item={item} index={i} />
            </FadeIn>
          ))}
        </div>

        {filtered.length === 0 && (
          <p className="text-center text-sm text-neutral-400 mt-6">No matching questions found.</p>
        )}
      </div>
    </section>
  );
}
