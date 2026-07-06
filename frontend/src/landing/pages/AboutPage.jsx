import { SectionHeading } from "../components/ui/SectionHeading";
import { Card } from "../components/ui/Card";
import { FadeIn } from "../components/animations/FadeIn";
import { Button } from "../components/ui/Button";
import { GradientText } from "../components/ui/GradientText";
import { ArrowRight, Target, Users, Shield, Zap } from "lucide-react";

const values = [
  { icon: Target, title: "Our Mission", description: "To democratize financial intelligence for every Indian household. We believe everyone deserves access to world-class financial tools, regardless of their wealth or financial literacy." },
  { icon: Users, title: "Who We Serve", description: "Salaried professionals, freelancers, small business owners, students, and families across India. Our platform supports 50+ Indian banks and is built specifically for Indian financial systems." },
  { icon: Shield, title: "Trust & Security", description: "We are registered as a Non-Banking Financial Company (NBFC) and comply with all RBI guidelines. Your data is encrypted with 256-bit AES and stored in India-based servers." },
  { icon: Zap, title: "Our Technology", description: "Our proprietary AI engine processes millions of transactions daily, learning from spending patterns to deliver personalized insights with 98.5% categorization accuracy." },
];

const team = [
  { name: "Arun Sharma", role: "CEO & Co-Founder", bio: "Ex-Google, IIT Bombay. 12 years in fintech and AI." },
  { name: "Priya Patel", role: "CTO & Co-Founder", bio: "Ex-Razorpay, IIT Delhi. Built payment systems processing ₹500Cr+ monthly." },
  { name: "Rahul Verma", role: "Head of Product", bio: "Ex-Cred, ISB. Product leader with 8 years in consumer fintech." },
  { name: "Ananya Gupta", role: "Head of AI", bio: "PhD in ML from IISc. Published 15+ papers in financial AI." },
];

export function AboutPage() {
  return (
    <div className="pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn className="text-center max-w-3xl mx-auto mb-16">
          <SectionHeading
            label="About Us"
            title="Building India's Financial Intelligence Platform"
            description="We're a team of engineers, designers, and finance experts on a mission to make every Indian financially confident."
          />
        </FadeIn>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
          {values.map((v, i) => (
            <FadeIn key={v.title} delay={i * 0.1}>
              <Card variant="default" className="h-full">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center mb-3">
                  <v.icon size={20} className="text-emerald-600" />
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">{v.title}</h3>
                <p className="text-sm text-neutral-500 leading-relaxed">{v.description}</p>
              </Card>
            </FadeIn>
          ))}
        </div>

        <FadeIn className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-neutral-900">
            Meet the <GradientText>Team</GradientText>
          </h2>
        </FadeIn>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {team.map((m, i) => (
            <FadeIn key={m.name} delay={i * 0.1}>
              <Card variant="default" className="text-center h-full">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-400 to-blue-400 flex items-center justify-center text-white text-xl font-bold mx-auto mb-3">
                  {m.name.split(" ").map((n) => n[0]).join("")}
                </div>
                <h3 className="text-base font-semibold text-neutral-900">{m.name}</h3>
                <p className="text-xs font-medium text-emerald-600 mb-2">{m.role}</p>
                <p className="text-xs text-neutral-400">{m.bio}</p>
              </Card>
            </FadeIn>
          ))}
        </div>

        <FadeIn className="text-center">
          <Button variant="primary" size="lg" href="/contact">
            Get in Touch <ArrowRight size={18} />
          </Button>
        </FadeIn>
      </div>
    </div>
  );
}
