import { useEffect } from 'react';
import PageHeader from '../../components/ui/PageHeader';
import StatusBadge from '../../components/ui/StatusBadge';
import useOrderStore from '../../store/orderStore';
import { isPastOrder, sortOrdersNewestFirst } from '../../utils/orderFilters';
import { formatCurrency, formatDate } from '../../utils/format';

const PastOrders = () => {
  const { orders, fetchOrders, isLoading, error } = useOrderStore();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const pastOrders = sortOrdersNewestFirst(orders.filter(isPastOrder));

  return (
    <div>
      <PageHeader
        title="Geçmiş Siparişler"
        subtitle="Teslim edilmiş siparişler — yeniden eskiye sıralı arşiv"
        actions={
          <button type="button" onClick={fetchOrders} className="erp-btn-secondary">
            Yenile
          </button>
        }
      />

      {error && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {error}
        </div>
      )}

      <div className="erp-card overflow-x-auto">
        {isLoading ? (
          <p className="p-6 text-sm text-gray-500">Yükleniyor...</p>
        ) : (
          <table className="erp-table">
            <thead>
              <tr>
                <th>Sipariş No</th>
                <th>Bayi</th>
                <th>Tarih</th>
                <th>İçerik</th>
                <th>Tutar</th>
                <th>Durum</th>
              </tr>
            </thead>
            <tbody>
              {pastOrders.map((order) => (
                <tr key={order.id}>
                  <td className="font-semibold tabular-nums">{order.order_number}</td>
                  <td>
                    <p className="font-semibold uppercase text-sm">{order.dealer_name}</p>
                    {order.dealer_code && (
                      <p className="text-[10px] text-gray-500 tabular-nums">{order.dealer_code}</p>
                    )}
                  </td>
                  <td className="text-gray-600 tabular-nums whitespace-nowrap">
                    {formatDate(order.order_date)}
                  </td>
                  <td className="text-gray-600 max-w-xs truncate">
                    {order.items
                      ?.map((i) => `${i.quantity}× ${i.product_name}`)
                      .join(', ') || '—'}
                  </td>
                  <td className="font-semibold tabular-nums">
                    {formatCurrency(order.total_amount || 0)}
                  </td>
                  <td>
                    <StatusBadge status={order.status} />
                  </td>
                </tr>
              ))}
              {pastOrders.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-8">
                    Teslim edilmiş sipariş bulunmamaktadır.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default PastOrders;
