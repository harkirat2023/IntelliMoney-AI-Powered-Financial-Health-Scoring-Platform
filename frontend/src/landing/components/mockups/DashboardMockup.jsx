import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from "recharts";
import { TrendingUp, Wallet, PiggyBank, AlertTriangle } from "lucide-react";

const chartData = [
  { category: "Food", amount: 8500 },
  { category: "Transport", amount: 3200 },
  { category: "Shopping", amount: 5400 },
  { category: "Bills", amount: 7200 },
  { category: "Health", amount: 2100 },
  { category: "Entertainment", amount: 3400 },
];

const stats = [
  { icon: Wallet, label: "Income", value: "\u20B985,000", color: "text-emerald-600" },
  { icon: TrendingUp, label: "Spending", value: "\u20B942,800", color: "text-blue-600" },
  { icon: PiggyBank, label: "Savings", value: "\u20B942,200", color: "text-violet-600" },
  { icon: AlertTriangle, label: "Anomalies", value: "2", color: "text-amber-600" },
];

const barColors = ["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"];

export function DashboardMockup() {
  return (
    <div className="bg-white rounded-2xl border border-neutral-200/80 shadow-xl overflow-hidden">
      <div className="bg-neutral-900/95 px-4 py-3 flex items-center gap-2">
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full bg-red-500/80" />
          <span className="w-3 h-3 rounded-full bg-amber-500/80" />
          <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
        </div>
        <span className="text-[11px] text-neutral-500 font-medium ml-2 tracking-wide">IntelliMoney Dashboard</span>
      </div>
      <div className="p-5">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5 mb-5">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-neutral-50/80 hover:bg-neutral-50 rounded-xl p-3 transition-colors">
              <stat.icon size={16} className={stat.color} />
              <div className="text-lg font-bold text-neutral-900 mt-1">{stat.value}</div>
              <div className="text-[11px] text-neutral-400 mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>
        <div className="h-40">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 5, bottom: 0, left: 5 }}>
              <XAxis dataKey="category" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis hide />
              <Bar dataKey="amount" radius={[6, 6, 0, 0]} animationDuration={1200}>
                {chartData.map((_entry, idx) => (
                  <Cell key={idx} fill={barColors[idx % barColors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
