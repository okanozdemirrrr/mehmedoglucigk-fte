const STATUS_CONFIG = {
  PENDING: { label: 'Onay Bekliyor', className: 'bg-orange-50 text-orange-800 border-orange-200' },
  PREPARING: { label: 'Hazırlanıyor', className: 'bg-blue-50 text-blue-800 border-blue-200' },
  ON_THE_WAY: { label: 'Yolda', className: 'bg-purple-50 text-purple-800 border-purple-200' },
  DELIVERED: { label: 'Teslim Edildi', className: 'bg-green-50 text-green-800 border-green-200' },
  DRAFT: { label: 'Taslak', className: 'bg-gray-50 text-gray-700 border-gray-200' },
  CANCELLED: { label: 'İptal', className: 'bg-red-50 text-red-800 border-red-200' },
};

const StatusBadge = ({ status }) => {
  const config = STATUS_CONFIG[status] || {
    label: status,
    className: 'bg-gray-50 text-gray-700 border-gray-200',
  };

  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs font-semibold border rounded-sm ${config.className}`}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
