import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../../components/ui/PageHeader';
import StatCard from '../../components/ui/StatCard';
import StatusBadge from '../../components/ui/StatusBadge';
import RevenueChart from '../../components/analytics/RevenueChart';
import useOrderStore from '../../store/orderStore';
import useAnalyticsStore from '../../store/analyticsStore';
import { formatCurrency, formatDate, formatTime } from '../../utils/format';
import { isActiveOrder, sortOrdersNewestFirst } from '../../utils/orderFilters';

const PERIODS = [
  { key: 'today', label: 'Bugün' },
  { key: 'this_week', label: 'Bu Hafta' },
  { key: 'this_month', label: 'Bu Ay' },
];

const EMPTY_KPIS = {
  total_revenue: '0',
  order_count: 0,
  pending_orders: 0,
  total_collection: '0',
  total_receivables: '0',
};

const AdminDashboard = () => {
  const { orders, fetchOrders, error: ordersError } = useOrderStore();
  const { analytics, isLoading, error: analyticsError, fetchDashboard } = useAnalyticsStore();
  const [period, setPeriod] = useState('this_month');

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    fetchDashboard(period);
  }, [period, fetchDashboard]);

  const kpis = analytics?.kpis || EMPTY_KPIS;
  const recentOrders = sortOrdersNewestFirst(orders.filter(isActiveOrder)).slice(0, 5);

  return (
    <div>
      <PageHeader
        title="Komuta Merkezi"
        subtitle="Finansal özet, ciro trendi ve son işlemler"
        actions={
          <div className="flex gap-1">
            {PERIODS.map(({ key, label }) => (
              <button
                key={key}
                type="button"
                onClick={() => setPeriod(key)}
                className={`px-3 py-1.5 text-xs font-semibold uppercase border rounded-sm ${
                  period === key
                    ? 'bg-bordo-800 text-white border-bordo-900'
                    : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        }
      />

      {(analyticsError || ordersError) && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {analyticsError || ordersError}
        </div>
      )}

      {isLoading ? (
        <p className="text-sm text-gray-500">Veriler yükleniyor...</p>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              label="Toplam Ciro"
              value={formatCurrency(kpis.total_revenue || 0)}
              subtext={`${analytics?.date_from} — ${analytics?.date_to}`}
            />
            <StatCard
              label="Sipariş Sayısı"
              value={String(kpis.order_count || 0)}
              subtext="Teslim edilen (seçilen dönem)"
            />
            <StatCard
              label="Tahsilat"
              value={formatCurrency(kpis.total_collection || 0)}
              subtext="Ödeme hareketleri"
            />
            <StatCard
              label="Toplam Alacak"
              value={formatCurrency(kpis.total_receivables || 0)}
              subtext={`Bekleyen: ${kpis.pending_orders || 0} sipariş`}
            />
          </div>

          <div className="mb-6">
            <RevenueChart data={analytics?.revenue_trend || []} />
          </div>

          <div className="erp-card mb-6">
            <div className="px-4 py-3 border-b border-gray-300 bg-gray-50">
              <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">
                Son İşlemler
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="erp-table">
                <thead>
                  <tr>
                    <th>Bayi</th>
                    <th>Tip</th>
                    <th>Açıklama</th>
                    <th>Tutar</th>
                    <th>Tarih</th>
                  </tr>
                </thead>
                <tbody>
                  {(analytics?.recent_activity || []).map((row, idx) => (
                    <tr key={idx}>
                      <td className="font-semibold uppercase text-sm">{row.dealer_name}</td>
                      <td>
                        <span
                          className={`text-xs font-semibold uppercase ${
                            row.type === 'payment' ? 'text-green-700' : 'text-gray-700'
                          }`}
                        >
                          {row.type === 'payment' ? 'Tahsilat' : 'Sipariş'}
                        </span>
                      </td>
                      <td className="text-gray-600">{row.description}</td>
                      <td className="font-semibold tabular-nums">{formatCurrency(row.amount)}</td>
                      <td className="text-gray-600 tabular-nums whitespace-nowrap">
                        {formatDate(row.timestamp)}
                      </td>
                    </tr>
                  ))}
                  {(analytics?.recent_activity || []).length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center text-gray-500 py-8">
                        Seçilen dönemde işlem kaydı bulunmamaktadır.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="erp-card">
            <div className="px-4 py-3 border-b border-gray-300 flex items-center justify-between bg-gray-50">
              <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">
                Son Gelen Talepler
              </h2>
              <Link to="/admin/siparisler" className="text-xs font-semibold text-bordo-800 hover:underline">
                Tümünü Gör →
              </Link>
            </div>
            <div className="divide-y divide-gray-200">
              {recentOrders.map((order) => (
                <div key={order.id} className="px-4 py-3 flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="text-sm font-bold uppercase">{order.dealer_name}</p>
                    <p className="text-xs text-gray-500">
                      {order.order_number} · {formatTime(order.order_date)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold tabular-nums">
                      {formatCurrency(order.total_amount || 0)}
                    </span>
                    <StatusBadge status={order.status} />
                  </div>
                </div>
              ))}
              {recentOrders.length === 0 && (
                <p className="px-4 py-8 text-center text-sm text-gray-500">
                  Henüz aktif sipariş bulunmamaktadır.
                </p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminDashboard;
