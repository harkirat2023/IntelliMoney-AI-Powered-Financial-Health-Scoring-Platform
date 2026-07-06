import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { currency } from "../../utils/format";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2", "#ec4899", "#f97316"];

export default function BarChartCard({ data, dataKey, color = "#2563eb", height = 260, title, colorByKey }) {
  return (
    <article className="dash-panel">
      {title && <h3 className="dash-panel-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf2" />
          <XAxis dataKey="category" tick={{ fontSize: 12, fill: "#65738b" }} />
          <YAxis tick={{ fontSize: 12, fill: "#65738b" }} />
          <Tooltip formatter={(value) => currency(value)} />
          <Bar dataKey={dataKey} radius={[6, 6, 0, 0]}>
            {data?.map((entry, index) => (
              <Cell key={index} fill={colorByKey ? entry.fill || COLORS[index % COLORS.length] : color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </article>
  );
}
