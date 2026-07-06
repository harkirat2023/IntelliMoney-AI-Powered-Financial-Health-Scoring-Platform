import { SectionHeading } from "../components/ui/SectionHeading";
import { Card } from "../components/ui/Card";
import { FadeIn } from "../components/animations/FadeIn";
import { StaggerList, StaggerItem } from "../components/animations/StaggerList";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { features } from "../data/features";
import * as Icons from "lucide-react";
import { ArrowRight, Sparkles } from "lucide-react";

const iconMap = {
  Banknote: Icons.Banknote,
  Sparkles: Icons.Sparkles,
  Brain: Icons.Brain,
  Shield: Icons.Shield,
  LineChart: Icons.LineChart,
  Goal: Icons.Goal,
};

export function FeaturesPage() {
  return (
    <div className="pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn>
          <div className="text-center mb-4">
            <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-semibold text-emerald-700 bg-emerald-100 rounded-full">
              <Sparkles size={12} />
              All Features
            </span>
          </div>
          <SectionHeading
            title="Everything IntelliMoney Offers"
            description="From AI-powered categorization to real-time fraud detection — every tool you need to master your finances."
          />
        </FadeIn>

        <StaggerList className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          {features.map((feature) => {
            const Icon = iconMap[feature.icon] || Icons.HelpCircle;
            return (
              <StaggerItem key={feature.title}>
                <Card variant="feature" hoverable className="h-full">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-4">
                    <Icon size={22} className="text-white" />
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-neutral-900">{feature.title}</h3>
                    {feature.badge && <Badge variant={feature.badgeVariant || "new"}>{feature.badge}</Badge>}
                  </div>
                  <p className="text-sm text-neutral-500 leading-relaxed">{feature.description}</p>
                </Card>
              </StaggerItem>
            );
          })}
        </StaggerList>

        <FadeIn className="text-center mt-12">
          <Button variant="primary" size="lg" href="/register">
            Get Started Free <ArrowRight size={18} />
          </Button>
        </FadeIn>
      </div>
    </div>
  );
}
