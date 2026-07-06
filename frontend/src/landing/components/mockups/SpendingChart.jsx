import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

const data = [
  { month: "Feb", amount: 32000 },
  { month: "Mar", amount: 28000 },
  { month: "Apr", amount: 35000 },
  { month: "May", amount: 26000 },
  { month: "Jun", amount: 22000 },
  { month: "Jul", amount: 18500 },
];

export function SpendingChart() {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="spendingGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
            <stop offset="100%" stopColor="#10b981" stopOpacity={0.0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fontSize: 12, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v / 1000}k`} />
        <Tooltip
          contentStyle={{ borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 4px 16px rgba(0,0,0,0.08)" }}
          formatter={(value) => [`₹${value.toLocaleString("en-IN")}`, "Spending"]}
        />
        <Area type="monotone" dataKey="amount" stroke="#10b981" strokeWidth={3} fill="url(#spendingGradient)" dot={{ fill: "#10b981", strokeWidth: 2, r: 4, stroke: "#fff" }} activeDot={{ r: 6, fill: "#10b981", stroke: "#fff", strokeWidth: 2 }} />
      </AreaChart>
    </ResponsiveContainer>
  );
}
