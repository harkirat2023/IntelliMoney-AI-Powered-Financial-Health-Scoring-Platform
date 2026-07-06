import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { DashboardMockup } from "../components/mockups/DashboardMockup";
import { ArrowRight, LayoutDashboard } from "lucide-react";

export function DashboardPreview() {
  return (
    <section className="py-16 md:py-24 bg-neutral-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          <FadeIn className="flex-1 text-center lg:text-left">
            <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 rounded-full mb-4">
              <LayoutDashboard size={12} />
              Powerful Dashboard
            </span>
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 tracking-tight">
              A <GradientText>Beautiful Dashboard</GradientText> That Makes Sense of Your Money
            </h2>
            <p className="mt-4 text-lg text-neutral-500 leading-relaxed max-w-md mx-auto lg:mx-0">
              See all your accounts in one place. Track income, expenses, savings, and anomalies — all beautifully visualized.
            </p>
            <div className="flex flex-wrap items-center gap-3 mt-6 justify-center lg:justify-start">
              <Button variant="primary" href="/register">
                Explore Dashboard <ArrowRight size={16} />
              </Button>
            </div>
          </FadeIn>
          <FadeIn direction="right" delay={0.2} className="flex-1 w-full max-w-xl">
            <DashboardMockup />
          </FadeIn>
        </div>
      </div>
    </section>
  );
}
