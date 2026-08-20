import SubNav from "./SubNav";

const navItems = [
  { path: "", label: "Overview", end: true },
  { path: "/upload", label: "Upload" },
  { path: "/review", label: "Review" },
  { path: "/history", label: "History" },
];

export default function ReceiptsLayout() {
  return <SubNav base="/app/receipts" items={navItems} />;
}