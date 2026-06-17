const PageHeader = ({ title, subtitle, actions }) => (
  <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between mb-6 pb-4 border-b border-gray-300">
    <div>
      <h1 className="text-lg font-bold text-gray-900 uppercase tracking-wide">{title}</h1>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
    {actions && <div className="flex gap-2 mt-2 sm:mt-0">{actions}</div>}
  </div>
);

export default PageHeader;
