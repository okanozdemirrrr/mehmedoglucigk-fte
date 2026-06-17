const StatCard = ({ label, value, subtext }) => (
  <div className="erp-card p-4">
    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">{label}</p>
    <p className="mt-2 text-2xl font-bold text-gray-900 tabular-nums">{value}</p>
    {subtext && <p className="mt-1 text-xs text-gray-500">{subtext}</p>}
  </div>
);

export default StatCard;
