import SubNav from "./SubNav";

const navItems = [
  { path: "", label: "Overview", end: true },
  { path: "/recommendations", label: "Recommendations" },
  { path: "/optimization", label: "Optimization" },
  { path: "/trends", label: "Trends" },
  { path: "/opportunities", label: "Opportunities" },
];

export default function BudgetIntelligenceLayout() {
  return <SubNav base="/app/budget-intelligence" items={navItems} />;
}