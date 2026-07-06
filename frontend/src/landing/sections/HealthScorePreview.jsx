import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { HealthScoreGauge } from "../components/mockups/HealthScoreGauge";
import { ArrowRight, Sparkles } from "lucide-react";

export function HealthScorePreview() {
  return (
    <section className="py-16 md:py-24 bg-gradient-to-br from-emerald-50 via-white to-blue-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <FadeIn className="flex-1 text-center lg:text-left">
            <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 rounded-full mb-4">
              <Sparkles size={12} />
              Financial Health Score
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight">
              Know Your <GradientText>Financial Health</GradientText> at a Glance
            </h2>
            <p className="mt-4 text-lg text-neutral-500 leading-relaxed max-w-md mx-auto lg:mx-0">
              Our AI analyzes your income, spending patterns, savings rate, and financial stability to generate a comprehensive health score from 0–100.
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-6">
              <Button variant="primary" href="/register">
                Check Your Score <ArrowRight size={16} />
              </Button>
            </div>
          </FadeIn>
          <FadeIn direction="right" delay={0.2}>
            <div className="glass-card rounded-2xl p-6">
              <HealthScoreGauge />
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  );
}
