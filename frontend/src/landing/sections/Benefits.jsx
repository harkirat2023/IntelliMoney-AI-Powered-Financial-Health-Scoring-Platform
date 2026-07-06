import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";
import { CheckCircle } from "lucide-react";

const benefits = [
  {
    title: "Save Thousands Annually",
    description: "Our users save an average of ₹1,20,000 per year by identifying wasteful subscriptions, optimizing bill payments, and reducing impulse spending.",
  },
  {
    title: "Never Miss a Bill",
    description: "AI-powered bill reminders and payment scheduling ensure you never pay late fees again. Supports all major Indian billers.",
  },
  {
    title: "Bank-Grade Security",
    description: "256-bit AES encryption, RBI-compliant data storage, and biometric authentication. Your financial data is protected with the highest security standards.",
  },
  {
    title: "Multi-Bank Aggregation",
    description: "Connect all your accounts — savings, current, credit cards, and investments — from 50+ Indian banks in one unified view.",
  },
  {
    title: "Tax-Smart Recommendations",
    description: "Get personalized tax-saving investment suggestions under Section 80C, 80D, and more. Maximize your refunds with AI-optimized strategies.",
  },
  {
    title: "Family Finance Management",
    description: "Invite family members, set shared goals, and manage household finances together. Perfect for young couples and joint families.",
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
