import { ArrowRight, PlayCircle, TrendingDown, Sparkles, Shield } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "../components/ui/Button";
import { Counter } from "../components/animations/Counter";
import { FadeIn } from "../components/animations/FadeIn";
import { GradientText } from "../components/ui/GradientText";
import { heroStats as stats } from "../data/stats";

export function HeroSection() {
  return (
    <section className="relative pt-28 pb-16 md:pt-36 md:pb-24 overflow-hidden hero-grid">
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-50/80 via-white to-white pointer-events-none" />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-400/50 to-transparent" />

      <div className="blob-gradient-1 absolute top-0 left-0 w-full h-full pointer-events-none" />
      <div className="blob-gradient-2 absolute top-0 left-0 w-full h-full pointer-events-none" />

      <div className="absolute top-20 left-1/4 w-[600px] h-[600px] bg-emerald-300/10 rounded-full blur-[120px] animate-pulse" style={{animationDuration: "8s"}} />
      <div className="absolute bottom-20 right-1/4 w-[500px] h-[500px] bg-blue-300/10 rounded-full blur-[120px] animate-pulse" style={{animationDuration: "10s", animationDelay: "2s"}} />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn className="text-center max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="inline-flex items-center gap-2 px-4 py-1.5 bg-emerald-100/80 backdrop-blur-sm rounded-full text-sm font-medium text-emerald-700 mb-6 border border-emerald-200/50"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            India&apos;s First AI Financial Intelligence Platform
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-neutral-900 tracking-tight leading-[1.05]"
          >
            Your Money,
            <br />
            <GradientText from="from-emerald-600" to="to-blue-600">Intelligently Managed</GradientText>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6 text-lg sm:text-xl text-neutral-500 leading-relaxed max-w-xl mx-auto"
          >
            Connect your bank accounts, let our AI analyze your spending, and get real-time insights to save smarter.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="flex items-center justify-center gap-3 sm:gap-4 mt-8"
          >
            <Button variant="gradient" size="lg" href="/register">
              Get Started Free
              <ArrowRight size={18} />
            </Button>
            <Button variant="secondary" size="lg" href="/features">
              <PlayCircle size={18} />
              See How It Works
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-wrap items-center justify-center gap-6 sm:gap-8 mt-12 pt-8 border-t border-neutral-200/60"
          >
            <div className="flex items-center gap-2 text-sm text-neutral-500">
              <Shield size={16} className="text-emerald-600" />
              <span>RBI Compliant</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-neutral-500">
              <TrendingDown size={16} className="text-emerald-600" />
              <span>Avg. 23% more savings</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-neutral-500">
              <Sparkles size={16} className="text-emerald-600" />
              <span>AI-Powered Insights</span>
            </div>
          </motion.div>
        </FadeIn>

        <FadeIn delay={0.5} className="mt-16">
          <div className="grid grid-cols-3 gap-6 max-w-2xl mx-auto">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center p-4 rounded-2xl bg-white/40 backdrop-blur-sm border border-white/50 hover-lift hover:bg-white/60">
                <div className="text-3xl md:text-4xl font-bold text-neutral-900">
                  <Counter target={stat.value} suffix={stat.suffix} />
                </div>
                <div className="text-sm text-neutral-500 mt-1.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </FadeIn>
      </div>
    </section>
  );
}
