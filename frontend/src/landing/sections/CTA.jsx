import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { ArrowRight, Shield, CreditCard, Clock } from "lucide-react";

export function CTA() {
  return (
    <section className="py-16 md:py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-emerald-700 to-blue-900" />
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-emerald-400/15 rounded-full blur-[100px]" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-400/15 rounded-full blur-[100px]" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-300/5 rounded-full blur-[120px]" />

      <div className="relative max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <FadeIn>
          <h2 className="text-3xl md:text-4xl font-bold text-white tracking-tight leading-[1.15]">
            Ready to Take Control of Your <GradientText from="from-emerald-300" to="to-blue-300">Financial Future</GradientText>?
          </h2>
          <p className="mt-4 text-lg text-emerald-100/70 leading-relaxed max-w-lg mx-auto">
            Join 50,000+ Indian users who have transformed their finances. Get started free in under 2 minutes.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 mt-8">
            <Button variant="secondary" size="xl" href="/register">
              Create Free Account <ArrowRight size={18} />
            </Button>
            <Button variant="ghost" size="xl" href="/features" className="text-white hover:text-white hover:bg-white/20">
              Learn More
            </Button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-6 mt-8 text-sm text-emerald-200/60">
            <div className="flex items-center gap-1.5">
              <Shield size={14} />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CreditCard size={14} />
              <span>Free forever plan available</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Clock size={14} />
              <span>Cancel anytime</span>
            </div>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
