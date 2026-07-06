import { motion } from "framer-motion";
import { Bot, User, Sparkles } from "lucide-react";

const messages = [
  { role: "assistant", text: "Hi! I'm your AI Financial Copilot. Ask me anything about your money." },
  { role: "user", text: "How much did I spend on food last month?" },
  { role: "assistant", text: "You spent \u20b912,450 on Food in June - 18% less than the previous month. Great job!" },
  { role: "user", text: "Can I afford a \u20b950,000 vacation in December?" },
  { role: "assistant", text: "Based on your savings rate of 24%, you'll have \u20b91,20,000 saved by December. That trip is well within reach!" },
];

export function CopilotChatMock() {
  return (
    <div className="bg-white rounded-2xl border border-neutral-200/80 shadow-lg p-5 max-w-md mx-auto backdrop-blur-sm">
      <div className="flex items-center gap-2 pb-3 mb-3 border-b border-neutral-100/80">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <div>
          <span className="font-semibold text-sm text-neutral-900">AI Financial Copilot</span>
          <span className="text-[11px] text-neutral-400 block -mt-0.5">Powered by IntelliMoney AI</span>
        </div>
        <span className="ml-auto flex items-center gap-1.5 bg-emerald-50 px-2 py-1 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-medium text-emerald-700">Active</span>
        </span>
      </div>
      <div className="space-y-3">
        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.5, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : ""}`}
          >
            {msg.role === "assistant" && (
              <div className="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot size={13} className="text-emerald-600" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-emerald-600 text-white rounded-tr-sm shadow-sm"
                  : "bg-neutral-100/80 text-neutral-700 rounded-tl-sm"
              }`}
            >
              {msg.text}
              {msg.role === "assistant" && i === 0 && (
                <span className="inline-flex ml-1">
                  <Sparkles size={12} className="text-emerald-500" />
                </span>
              )}
            </div>
            {msg.role === "user" && (
              <div className="w-7 h-7 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                <User size={13} className="text-white" />
              </div>
            )}
          </motion.div>
        ))}
      </div>
      <div className="mt-3 pt-3 border-t border-neutral-100/80">
        <div className="flex gap-2">
          <div className="flex-1 h-9 rounded-xl bg-neutral-100/50 border border-neutral-200/50" />
          <div className="w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2L11 13" /><path d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
