import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { SpendingChart } from "../components/mockups/SpendingChart";
import { ArrowRight, TrendingDown } from "lucide-react";

export function SpendingPreview() {
  return (
    <section className="py-16 md:py-24 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <FadeIn direction="left" className="flex-1 w-full max-w-lg">
            <div className="glass-card rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-semibold text-neutral-700">Monthly Spending Trend</span>
                <span className="text-xs font-medium text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">-15% vs last quarter</span>
              </div>
              <SpendingChart />
            </div>
          </FadeIn>
          <FadeIn className="flex-1 text-center lg:text-left">
            <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 rounded-full mb-4">
              <TrendingDown size={12} />
              Smart Tracking
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight">
              Watch Your <GradientText>Spending</GradientText> Drop Month Over Month
            </h2>
            <p className="mt-4 text-lg text-neutral-500 leading-relaxed max-w-md mx-auto lg:mx-0">
              Our AI identifies wasteful spending patterns and gives you actionable recommendations. Users typically reduce expenses by 23% in the first 3 months.
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-6 justify-center lg:justify-start">
              <Button variant="primary" href="/register">
                Start Saving <ArrowRight size={16} />
              </Button>
            </div>
          </FadeIn>
        </div>
      </div>
    </section>
  );
}
