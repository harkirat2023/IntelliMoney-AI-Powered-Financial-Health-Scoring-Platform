import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";

const sections = [
  {
    title: "Acceptance of Terms",
    content: "By accessing or using IntelliMoney, you agree to be bound by these Terms of Service. If you do not agree, please do not use the platform. We reserve the right to update these terms at any time with 30 days notice.",
  },
  {
    title: "Service Description",
    content: "IntelliMoney provides AI-powered financial analysis, spending categorization, budget tracking, and personalized insights. We are a financial intelligence platform, not a financial advisor. Decisions based on our insights are your responsibility.",
  },
  {
    title: "Account Registration",
    content: "You must provide accurate information when creating an account. You are responsible for maintaining the confidentiality of your credentials. One person per account — sharing accounts is prohibited.",
  },
  {
    title: "Subscription & Billing",
    content: "We offer a free tier with basic features and paid subscriptions with premium features. Billing is monthly or annually as selected. You can cancel anytime — cancellations take effect at the end of the current billing cycle.",
  },
  {
    title: "Data Security",
    content: "We implement industry-standard security measures to protect your data. However, no system is 100% secure. You agree to notify us immediately of any unauthorized access. We are not liable for damages from security breaches beyond our reasonable control.",
  },
  {
    title: "Acceptable Use",
    content: "You agree not to misuse the platform for illegal activities, money laundering, or fraud. We reserve the right to suspend accounts that violate these terms or are flagged by our compliance systems.",
  },
  {
    title: "Limitation of Liability",
    content: "IntelliMoney is provided 'as is' without warranties. Our liability is limited to the amount you paid in the last 12 months. We are not responsible for financial losses resulting from investment decisions or incorrect transaction categorization.",
  },
  {
    title: "Termination",
    content: "You can delete your account at any time from settings. We may suspend or terminate accounts for violations of these terms. Upon termination, your data will be deleted within 30 days.",
  },
  {
    title: "Governing Law",
    content: "These terms are governed by the laws of India. Disputes shall be resolved in the courts of Bangalore, Karnataka.",
  },
];

export function TermsPage() {
  return (
    <div className="pt-24 pb-16">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn>
          <SectionHeading
            label="Terms of Service"
            title="How We Work Together"
            description="Last updated: July 2025"
            align="left"
          />
        </FadeIn>

        <div className="mt-8 space-y-8">
          {sections.map((s, i) => (
            <FadeIn key={s.title} delay={i * 0.05}>
              <div>
                <h2 className="text-lg font-semibold text-neutral-900 mb-2">{s.title}</h2>
                <p className="text-sm text-neutral-500 leading-relaxed">{s.content}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </div>
  );
}
