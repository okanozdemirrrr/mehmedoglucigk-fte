import { useEffect, useState } from 'react';
import PageHeader from '../../components/ui/PageHeader';
import StatusBadge from '../../components/ui/StatusBadge';
import OptionTags from '../../components/orders/OptionTags';
import useOrderStore from '../../store/orderStore';
import { formatCurrency, formatDate, formatTime } from '../../utils/format';
import { isActiveOrder, sortOrdersNewestFirst } from '../../utils/orderFilters';

const AdminOrders = () => {
  const { orders, fetchOrders, updateOrderStatus, isLoading, error } = useOrderStore();
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const sortedOrders = sortOrdersNewestFirst(orders.filter(isActiveOrder));

  const handleStatusUpdate = async (orderId, action) => {
    setActionError(null);
    try {
      await updateOrderStatus(orderId, action);
    } catch (err) {
      setActionError(
        err.response?.data?.error ||
          err.response?.data?.detail ||
          'Sipariş durumu güncellenemedi.'
      );
    }
  };

  return (
    <div>
      <PageHeader
        title="Gelen Talepler"
        subtitle="Aktif operasyonlar — onay bekleyen, hazırlanan ve yoldaki siparişler"
        actions={
          <button type="button" onClick={fetchOrders} className="erp-btn-secondary">
            Yenile
          </button>
        }
      />

      {(error || actionError) && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {actionError || error}
        </div>
      )}

      <div className="space-y-3">
        {isLoading && <p className="text-sm text-gray-500 p-4">Veriler yükleniyor...</p>}

        {!isLoading && sortedOrders.length === 0 && (
          <div className="erp-card p-8 text-center text-gray-500">
            Henüz aktif sipariş bulunmamaktadır.
          </div>
        )}

        {sortedOrders.map((order) => (
          <div key={order.id} className="erp-card p-4">
            <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-bordo-800">
                    Bayi
                  </span>
                  <h3 className="text-lg font-bold uppercase tracking-wide text-gray-900">
                    {order.dealer_name}
                  </h3>
                  <span className="text-sm text-gray-500 tabular-nums">
                    — {formatTime(order.order_date)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1 tabular-nums">
                  {order.order_number}
                  {order.dealer_code && ` · ${order.dealer_code}`}
                  {' · '}
                  {formatDate(order.order_date)}
                </p>

                {order.items?.length > 0 && (
                  <div className="mt-3 space-y-2 border-t border-gray-200 pt-3">
                    {order.items.map((item, idx) => (
                      <div key={idx} className="text-sm">
                        <span className="font-semibold text-gray-800">
                          {item.quantity} {item.product_name}
                        </span>
                        <span className="text-gray-500 ml-2 tabular-nums">
                          {formatCurrency(item.unit_price || 0)}/birim
                        </span>
                        <OptionTags item={item} />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="flex flex-col items-start lg:items-end gap-2 flex-shrink-0">
                <p className="text-xl font-bold tabular-nums text-gray-900">
                  {formatCurrency(order.total_amount || 0)}
                </p>
                <StatusBadge status={order.status} />
                <div className="flex flex-wrap gap-1 mt-1">
                  {order.status === 'PENDING' && (
                    <button type="button" onClick={() => handleStatusUpdate(order.id, 'approve')} className="erp-btn-secondary">
                      Hazırlanıyor Yap
                    </button>
                  )}
                  {order.status === 'PREPARING' && (
                    <button type="button" onClick={() => handleStatusUpdate(order.id, 'ship')} className="erp-btn-secondary">
                      Yola Çıkar
                    </button>
                  )}
                  {order.status === 'ON_THE_WAY' && (
                    <span className="text-xs text-gray-500 uppercase">
                      Bayi teslim onayı bekleniyor
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminOrders;
