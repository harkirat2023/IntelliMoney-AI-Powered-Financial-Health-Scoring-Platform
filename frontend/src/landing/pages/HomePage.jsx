import { HeroSection } from "../sections/HeroSection";
import { TrustedBy } from "../sections/TrustedBy";
import { Features } from "../sections/Features";
import { HowItWorks } from "../sections/HowItWorks";
import { HealthScorePreview } from "../sections/HealthScorePreview";
import { SpendingPreview } from "../sections/SpendingPreview";
import { CopilotPreview } from "../sections/CopilotPreview";
import { DashboardPreview } from "../sections/DashboardPreview";
import { Benefits } from "../sections/Benefits";
import { Testimonials } from "../sections/Testimonials";
import { FAQ } from "../sections/FAQ";
import { CTA } from "../sections/CTA";

export function HomePage() {
  return (
    <>
      <HeroSection />
      <TrustedBy />
      <Features />
      <HowItWorks />
      <HealthScorePreview />
      <SpendingPreview />
      <CopilotPreview />
      <DashboardPreview />
      <Benefits />
      <Testimonials />
      <FAQ />
      <CTA />
    </>
  );
}
