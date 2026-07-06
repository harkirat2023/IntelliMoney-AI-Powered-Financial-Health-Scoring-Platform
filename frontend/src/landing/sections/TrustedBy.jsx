import { Building2, Landmark, Store, Heart, GraduationCap, Briefcase } from "lucide-react";

const logos = [
  { icon: Building2, label: "Axis Bank" },
  { icon: Landmark, label: "HDFC" },
  { icon: Store, label: "Reliance" },
  { icon: Heart, label: "Apollo" },
  { icon: GraduationCap, label: "IIT Delhi" },
  { icon: Briefcase, label: "Infosys" },
];

export function TrustedBy() {
  return (
    <section className="py-14 bg-neutral-50/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-[11px] font-semibold text-neutral-400 uppercase tracking-[0.15em] mb-8">
          Trusted by leading Indian enterprises
        </p>
        <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
          {logos.map((logo) => (
            <div
              key={logo.label}
              className="group flex items-center gap-2.5 px-5 py-2.5 rounded-xl text-neutral-400 hover:text-neutral-600 hover:bg-white/80 transition-all duration-300"
            >
              <div className="w-10 h-10 rounded-xl bg-neutral-100 group-hover:bg-emerald-50 flex items-center justify-center transition-colors">
                <logo.icon size={20} className="group-hover:text-emerald-600 transition-colors" />
              </div>
              <span className="text-sm font-semibold">{logo.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
