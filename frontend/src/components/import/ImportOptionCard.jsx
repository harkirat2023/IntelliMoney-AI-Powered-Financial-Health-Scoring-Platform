import { motion } from "framer-motion";

export default function ImportOptionCard({ icon: Icon, title, description, estimate, selected, onSelect }) {
  return (
    <motion.button
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      onClick={onSelect}
      className={`w-full text-left p-5 rounded-xl border-2 transition-all duration-200 ${
        selected
          ? "border-emerald-500 bg-emerald-50/50 shadow-md shadow-emerald-100/50"
          : "border-neutral-200 bg-white hover:border-emerald-200 hover:shadow-sm"
      }`}
    >
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
          selected ? "bg-emerald-100 text-emerald-600" : "bg-neutral-100 text-neutral-500"
        }`}>
          <Icon size={24} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-neutral-900">{title}</h3>
            {selected && (
              <span className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center">
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-neutral-500">{description}</p>
          {estimate && (
            <p className="mt-2 text-xs font-medium text-emerald-700 bg-emerald-50 inline-block px-2.5 py-1 rounded-full">
              {estimate}
            </p>
          )}
        </div>
      </div>
    </motion.button>
  );
}
