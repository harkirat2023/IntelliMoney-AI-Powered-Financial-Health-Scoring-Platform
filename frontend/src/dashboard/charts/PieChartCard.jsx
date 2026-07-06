import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { currency } from "../../utils/format";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#ec4899", "#f97316"];

export default function PieChartCard({ data, dataKey = "amount", nameKey = "category", height = 280, title, innerRadius = 60, outerRadius = 100 }) {
  return (
    <article className="dash-panel">
      {title && <h3 className="dash-panel-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie data={data} dataKey={dataKey} nameKey={nameKey} innerRadius={innerRadius} outerRadius={outerRadius} paddingAngle={2}>
            {data?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
          </Pie>
          <Tooltip formatter={(value) => currency(value)} />
        </PieChart>
      </ResponsiveContainer>
      <div className="pie-legend">
        {data?.map((item, i) => (
          <div className="pie-legend-item" key={i}>
            <span className="pie-dot" style={{ background: COLORS[i % COLORS.length] }} />
            <span>{item[nameKey]}</span>
            <span className="pie-value">{currency(item[dataKey])}</span>
          </div>
        ))}
      </div>
    </article>
  );
}
