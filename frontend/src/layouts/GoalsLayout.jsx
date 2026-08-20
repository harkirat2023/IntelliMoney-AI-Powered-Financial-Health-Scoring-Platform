import SubNav from "./SubNav";

const navItems = [
  { path: "", label: "Overview", end: true },
  { path: "/create", label: "Create Goal" },
  { path: "/recommendations", label: "Recommendations" },
  { path: "/progress", label: "Progress" },
  { path: "/history", label: "History" },
];

export default function GoalsLayout() {
  return <SubNav base="/app/goals" items={navItems} />;
}