import SubNav from "./SubNav";

const navItems = [
  { path: "", label: "Chat", end: true },
  { path: "/history", label: "History" },
  { path: "/settings", label: "Settings" },
];

export default function CopilotLayout() {
  return <SubNav base="/app/copilot" items={navItems} />;
}