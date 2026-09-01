import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";
import { CheckCircle } from "lucide-react";

const benefits = [
  {
    title: "See Recurring Costs",
    description: "Track subscriptions and recurring expenses so you can spot commitments that deserve a closer look.",
  },
  {
    title: "Stay Aware of Due Dates",
    description: "Keep recurring expenses and subscriptions visible alongside their expected payment dates.",
  },
  {
    title: "User-Scoped Data",
    description: "Clerk authentication and user-scoped data access keep one customer's financial records separate from another's.",
  },
  {
    title: "Sandbox Account Aggregation",
    description: "Explore the optional Setu AA sandbox demonstration with simulated data; live bank connectivity is not offered.",
  },
  {
    title: "Clear Financial Insights",
    description: "Review deterministic budget, cash-flow, health, goal, and spending insights based on your stored data.",
  },
  {
    title: "Personal Finance Goals",
    description: "Create and track your own savings goals with progress, projections, and practical recommendations.",
  },
];

export function Benefits() {
  return (
    <section className="py-16 md:py-24 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="Benefits"
          title="Why Indian Users Love IntelliMoney"
          description="Designed for Indian households, salaried professionals, and small businesses."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {benefits.map((benefit, i) => (
            <FadeIn key={benefit.title} delay={i * 0.08}>
              <div className="group flex gap-4 p-5 rounded-2xl border border-neutral-100 hover:border-emerald-100 hover:shadow-md hover:shadow-emerald-100/10 transition-all duration-300">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 group-hover:bg-emerald-200 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors">
                  <CheckCircle size={20} className="text-emerald-600" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-neutral-900 mb-1">{benefit.title}</h3>
                  <p className="text-sm text-neutral-500 leading-relaxed">{benefit.description}</p>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
