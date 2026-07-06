import { SectionHeading } from "../components/ui/SectionHeading";
import { Card } from "../components/ui/Card";
import { StaggerList, StaggerItem } from "../components/animations/StaggerList";
import { testimonials } from "../data/testimonials";
import { Star } from "lucide-react";

const AVATAR_GRADIENTS = [
  "from-emerald-500 to-emerald-700",
  "from-blue-500 to-blue-700",
  "from-violet-500 to-violet-700",
  "from-amber-500 to-amber-700",
  "from-rose-500 to-rose-700",
  "from-cyan-500 to-cyan-700",
];

export function Testimonials() {
  return (
    <section className="py-16 md:py-24 bg-neutral-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          label="Testimonials"
          title="What Our Users Say"
          description="Join 50,000+ Indian users who have transformed their relationship with money."
        />

        <StaggerList className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((t, idx) => (
            <StaggerItem key={t.name}>
              <Card variant="default" className="group h-full flex flex-col border border-neutral-200/80 hover:border-emerald-200/80 hover:shadow-xl hover:shadow-emerald-100/10 hover:-translate-y-1 transition-all duration-500">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={14} className={i < t.rating ? "text-amber-400 fill-amber-400" : "text-neutral-200"} />
                  ))}
                </div>
                <p className="text-sm text-neutral-600 leading-relaxed flex-1 italic">&ldquo;{t.quote}&rdquo;</p>
                <div className="flex items-center gap-3 mt-auto pt-4 border-t border-neutral-100/80">
                  <div className={`w-11 h-11 rounded-full bg-gradient-to-br ${AVATAR_GRADIENTS[idx % AVATAR_GRADIENTS.length]} flex items-center justify-center text-white text-sm font-bold shadow-sm`}>
                    {t.name.split(" ").map((n) => n[0]).join("")}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-neutral-900">{t.name}</div>
                    <div className="text-xs text-neutral-400">{t.role}</div>
                  </div>
                </div>
              </Card>
            </StaggerItem>
          ))}
        </StaggerList>
      </div>
    </section>
  );
}
