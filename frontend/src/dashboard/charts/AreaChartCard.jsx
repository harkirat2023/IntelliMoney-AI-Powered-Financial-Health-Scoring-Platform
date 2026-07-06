import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { currency } from "../../utils/format";

export default function AreaChartCard({ data, dataKey, color = "#2563eb", height = 260, title }) {
  return (
    <article className="dash-panel">
      {title && <h3 className="dash-panel-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`grad-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5eaf2" />
          <XAxis dataKey="month" tick={{ fontSize: 12, fill: "#65738b" }} />
          <YAxis tick={{ fontSize: 12, fill: "#65738b" }} />
          <Tooltip formatter={(value) => currency(value)} />
          <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} fill={`url(#grad-${dataKey})`} />
        </AreaChart>
      </ResponsiveContainer>
    </article>
  );
}
