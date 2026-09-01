import { LogIn, Building2, Import, Bot, LineChart } from "lucide-react";

export const steps = [
  {
    step: 1,
    icon: LogIn,
    title: "Sign Up",
    description: "Create your free account in under 30 seconds. No credit card required.",
    gradient: "from-emerald-400 to-emerald-500",
  },
  {
    step: 2,
    icon: Building2,
    title: "Choose Your Data Source",
    description:
      "Add expenses manually or explore the optional Setu Account Aggregator sandbox demo with simulated data.",
    gradient: "from-blue-400 to-blue-500",
  },
  {
    step: 3,
    icon: Import,
    title: "Import Your Transactions",
    description:
      "Optionally import approved sandbox data, then review and categorize transactions before relying on them.",
    gradient: "from-violet-400 to-violet-500",
  },
  {
    step: 4,
    icon: Bot,
    title: "Automatic AI Categorization",
    description:
      "Every expense is tagged intelligently. Watch your spending patterns reveal themselves in real time.",
    gradient: "from-amber-400 to-amber-500",
  },
  {
    step: 5,
    icon: LineChart,
    title: "Real-Time Insights",
    description:
      "Get your financial health score, budget alerts, anomaly detection, and AI-powered recommendations daily.",
    gradient: "from-rose-400 to-rose-500",
  },
];
