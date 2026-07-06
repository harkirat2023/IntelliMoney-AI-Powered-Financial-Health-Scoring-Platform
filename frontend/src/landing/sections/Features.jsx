import { SectionHeading } from "../components/ui/SectionHeading";
import { Card } from "../components/ui/Card";
import { StaggerList, StaggerItem } from "../components/animations/StaggerList";
import { Badge } from "../components/ui/Badge";
import { features } from "../data/features";
import * as Icons from "lucide-react";

const iconMap = {
  Landmark: Icons.Landmark,
  Banknote: Icons.Banknote,
  Sparkles: Icons.Sparkles,
  Brain: Icons.Brain,
  Shield: Icons.Shield,
  LineChart: Icons.LineChart,
  Goal: Icons.Goal,
};

export function Features() {
  return (
    <section id="features" className="py-16 md:py-24 bg-white scroll-mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="Features"
          title="Everything you need to master your finances"
          description="From AI-powered categorization to real-time fraud detection — IntelliMoney gives you the tools to take control."
        />

        <StaggerList className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = iconMap[feature.icon] || Icons.HelpCircle;
            return (
              <StaggerItem key={feature.title}>
                <Card variant="default" className="group h-full border border-neutral-100/80 hover:border-emerald-200/80 hover:shadow-xl hover:shadow-emerald-100/20 hover:-translate-y-1 transition-all duration-500">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center mb-4 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-emerald-500/20 transition-all duration-500">
                    <Icon size={24} className="text-white" />
                  </div>
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <h3 className="text-lg font-semibold text-neutral-900 group-hover:text-emerald-700 transition-colors">{feature.title}</h3>
                    {feature.badge && <Badge variant={feature.badgeVariant || "new"}>{feature.badge}</Badge>}
                  </div>
                  <p className="text-sm text-neutral-500 leading-relaxed group-hover:text-neutral-600 transition-colors">{feature.description}</p>
                </Card>
              </StaggerItem>
            );
          })}
        </StaggerList>
      </div>
    </section>
  );
}
