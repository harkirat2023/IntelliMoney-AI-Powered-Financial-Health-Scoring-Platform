import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { currency } from "../../utils/format";

export default function LineChartCard({ data, lines, height = 260, title }) {
  return (
    <article className="dash-panel">
      {title && <h3 className="dash-panel-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf2" />
          <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#65738b" }} />
          <YAxis tick={{ fontSize: 12, fill: "#65738b" }} />
          <Tooltip formatter={(value) => currency(value)} />
          {lines.map((line) => (
            <Line key={line.dataKey} type="monotone" dataKey={line.dataKey} stroke={line.color} strokeWidth={2} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </article>
  );
}
