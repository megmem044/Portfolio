interface StatsPanelProps {
  total: number;
  active: number;
  completed: number;
}

export function StatsPanel({ total, active, completed }: StatsPanelProps) {
  const stats = [
    { label: 'Total', value: total, className: '' },
    { label: 'Active', value: active, className: 'stat-active' },
    { label: 'Completed', value: completed, className: 'stat-done' },
  ];
  return <section className="stats-container">{stats.map((stat) => (
    <div className="stat-card" key={stat.label}>
      <span className={`stat-number ${stat.className}`}>{stat.value}</span>
      <span className="stat-label">{stat.label}</span>
    </div>
  ))}</section>;
}