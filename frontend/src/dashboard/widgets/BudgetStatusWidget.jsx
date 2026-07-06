export default function BudgetStatusWidget({ data }) {
  if (!data) return null;
  return (
    <article className="dash-panel">
      <h3 className="dash-panel-title">Budget Status</h3>
      <div className="budget-summary-strip">
        <div className="budget-summary-item">
          <span className="budget-summary-count">{data.on_track}</span>
          <span className="budget-summary-label safe">On Track</span>
        </div>
        <div className="budget-summary-item">
          <span className="budget-summary-count">{data.warning}</span>
          <span className="budget-summary-label warning">Warning</span>
        </div>
        <div className="budget-summary-item">
          <span className="budget-summary-count">{data.over}</span>
          <span className="budget-summary-label over">Over</span>
        </div>
      </div>
      <div className="budget-mini-list">
        {data.budgets?.slice(0, 5).map((b, i) => (
          <div className={`budget-mini-item ${b.state}`} key={i}>
            <span className="budget-mini-cat">{b.category}</span>
            <div className="budget-mini-bar">
              <div className="budget-mini-fill" style={{ width: `${Math.min(b.percentage_used || 0, 100)}%` }} />
            </div>
            <span className="budget-mini-pct">{b.percentage_used?.toFixed(0)}%</span>
          </div>
        ))}
      </div>
    </article>
  );
}
