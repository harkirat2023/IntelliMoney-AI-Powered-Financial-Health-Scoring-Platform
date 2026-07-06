import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";

const sections = [
  {
    title: "Information We Collect",
    content: "We collect information you provide directly, including your name, email address, phone number, bank account details, and transaction data. We also automatically collect usage data such as IP address, browser type, and device information to improve our services.",
  },
  {
    title: "How We Use Your Data",
    content: "Your data is used to provide financial analysis, categorize transactions, generate insights, detect fraud, and improve our AI models. We never sell your personal data to third parties. Aggregated, anonymized data may be used for benchmark analytics.",
  },
  {
    title: "Data Storage & Security",
    content: "All data is stored on India-based servers compliant with RBI guidelines. We use 256-bit AES encryption for data at rest and TLS 1.3 for data in transit. Access to your data is restricted to authorized personnel only.",
  },
  {
    title: "Bank Account & Transaction Data",
    content: "Your bank credentials are never stored on our servers. We use RBI-approved account aggregator framework for secure data fetching. Transaction data is encrypted and can be deleted at any time from your account settings.",
  },
  {
    title: "Data Retention",
    content: "We retain your data for as long as your account is active. You can request complete data deletion at any time. Deleted data is permanently removed within 30 days.",
  },
  {
    title: "Your Rights",
    content: "Under Indian data protection laws, you have the right to access, correct, delete, and port your data. You can manage these settings from your account dashboard or by contacting our support team.",
  },
  {
    title: "Cookies",
    content: "We use essential cookies for authentication and security. Optional analytics cookies help us improve the platform. You can manage cookie preferences from your browser settings.",
  },
  {
    title: "Third-Party Services",
    content: "We integrate with RBI-approved account aggregators and payment gateways. These partners are contractually bound to protect your data and comply with Indian data protection regulations.",
  },
];

export function PrivacyPage() {
  return (
    <div className="pt-24 pb-16">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <FadeIn>
          <SectionHeading
            label="Privacy Policy"
            title="Your Privacy Matters"
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
