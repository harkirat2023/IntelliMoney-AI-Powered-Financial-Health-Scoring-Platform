import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";

const score = 78;
const color = score >= 70 ? "#10b981" : score >= 45 ? "#f59e0b" : "#ef4444";
const data = [{ name: "Score", value: score, fill: color }];

const metrics = [
  { label: "Savings Rate", value: "65%", sub: "Excellent" },
  { label: "Budget Adherence", value: "82%", sub: "Good" },
  { label: "Stability", value: "71%", sub: "Stable" },
];

export function HealthScoreGauge() {
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="50%"
            innerRadius="72%"
            outerRadius="100%"
            barSize={16}
            data={data}
            startAngle={225}
            endAngle={-45}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
            <RadialBar dataKey="value" cornerRadius={8} animationDuration={1500} background={{ fill: "#f1f5f9" }} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold" style={{ color }}>{score}</span>
          <span className="text-xs font-medium text-neutral-400 mt-0.5">out of 100</span>
        </div>
      </div>
      <div className="flex gap-6 mt-5 pt-4 border-t border-neutral-100 w-full justify-center">
        {metrics.map((item) => (
          <div key={item.label} className="text-center">
            <div className="text-sm font-bold text-neutral-900">{item.value}</div>
            <div className="text-[10px] text-neutral-400 uppercase tracking-wider mt-0.5">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
