import SubNav from "./SubNav";

const navItems = [
  { path: "", label: "Overview", end: true },
  { path: "/history", label: "History" },
  { path: "/trends", label: "Trends" },
  { path: "/recommendations", label: "Recommendations" },
  { path: "/risk", label: "Risk" },
];

export default function HealthLayout() {
  return <SubNav base="/app/health" items={navItems} />;
}