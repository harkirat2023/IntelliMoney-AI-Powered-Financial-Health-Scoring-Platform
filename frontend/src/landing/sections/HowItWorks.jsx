import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";
import { steps as howItWorks } from "../data/howItWorks";

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-16 md:py-24 bg-neutral-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="How It Works"
          title="Get started in 5 minutes"
          description="No complicated setup. Just connect, relax, and let AI do the heavy lifting."
        />

        <div className="relative">
          <div className="hidden lg:block absolute top-[52px] left-[10%] right-[10%] h-[2px] bg-gradient-to-r from-emerald-200 via-emerald-400 to-blue-300" style={{ width: "80%", margin: "0 auto" }} />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-6">
            {howItWorks.map((step, i) => {
              const Icon = step.icon;
              return (
                <FadeIn key={step.title} delay={i * 0.1} className="relative flex flex-col items-center">
                  <div className={`relative z-10 w-16 h-16 rounded-2xl shadow-lg flex items-center justify-center mb-4 bg-gradient-to-br ${step.gradient} hover:shadow-xl hover:-translate-y-1 hover:scale-105 transition-all duration-300`}>
                    <Icon size={24} className="text-white" />
                    <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-white border-2 border-emerald-200 flex items-center justify-center text-[10px] font-bold text-emerald-700 shadow-sm">
                      {step.step}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-neutral-900 mb-1.5">{step.title}</h3>
                  <p className="text-xs text-neutral-500 leading-relaxed text-center max-w-[200px]">{step.description}</p>
                </FadeIn>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
