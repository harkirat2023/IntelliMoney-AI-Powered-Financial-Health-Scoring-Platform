import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { CopilotChatMock } from "../components/mockups/CopilotChatMock";
import { ArrowRight, Bot } from "lucide-react";

export function CopilotPreview() {
  return (
    <section className="py-16 md:py-24 bg-gradient-to-br from-neutral-900 to-neutral-800 text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <FadeIn className="flex-1 text-center lg:text-left">
            <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-emerald-300 bg-emerald-900/50 rounded-full mb-4">
              <Bot size={12} />
              AI Financial Copilot
            </span>
            <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
              Meet Your <GradientText from="from-emerald-400" to="to-blue-400">AI Financial Copilot</GradientText>
            </h2>
            <p className="mt-4 text-lg text-neutral-400 leading-relaxed max-w-md mx-auto lg:mx-0">
              Ask anything about your money. Get instant answers, personalized advice, and proactive alerts — like having a CFA in your pocket.
            </p>
            <ul className="mt-6 space-y-3 text-sm text-neutral-400">
              {[
                "Real-time spending analysis",
                "Savings goal tracking & alerts",
                "Fraud detection & anomaly flags",
                "Investment recommendations",
              ].map((item) => (
                <li key={item} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  {item}
                </li>
              ))}
            </ul>
            <div className="flex flex-wrap items-center gap-3 mt-6 justify-center lg:justify-start">
              <Button variant="gradient" href="/register">
                Try the Copilot <ArrowRight size={16} />
              </Button>
            </div>
          </FadeIn>
          <FadeIn direction="right" delay={0.2}>
            <CopilotChatMock />
          </FadeIn>
        </div>
      </div>
    </section>
  );
}
