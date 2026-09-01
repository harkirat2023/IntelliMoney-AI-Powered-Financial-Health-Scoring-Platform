import { SectionHeading } from "../components/ui/SectionHeading";
import { FadeIn } from "../components/animations/FadeIn";

const sections = [
  {
    title: "Information We Collect",
    content: "We collect the account and financial information you provide to deliver the application's personal-finance features. The optional Account Aggregator experience uses simulated sandbox data and is not a live banking connection.",
  },
  {
    title: "How We Use Your Data",
    content: "Your data is used to provide financial analysis, categorization, and insights within your account. Deterministic backend services remain the source of truth for financial calculations.",
  },
  {
    title: "Data Storage & Security",
    content: "Access to application data is authenticated and scoped to the signed-in user. Do not treat this demonstration application as a statement of banking, regulatory, or data-residency certification.",
  },
  {
    title: "Bank Account & Transaction Data",
    content: "The optional Account Aggregator flow is a Setu sandbox demonstration with simulated data. It does not collect bank credentials or connect to production bank accounts.",
  },
  {
    title: "Data Retention",
    content: "Data-retention and deletion commitments require deployment-owner review before they are presented as contractual promises.",
  },
  {
    title: "Your Rights",
    content: "For privacy or data-access requests, contact the deployment owner. This page does not replace a reviewed legal privacy notice.",
  },
  {
    title: "Cookies",
    content: "We use essential cookies for authentication and security. Optional analytics cookies help us improve the platform. You can manage cookie preferences from your browser settings.",
  },
  {
    title: "Third-Party Services",
    content: "The application includes a Setu Account Aggregator sandbox adapter for demonstration. It does not offer payment processing or production banking integration.",
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
