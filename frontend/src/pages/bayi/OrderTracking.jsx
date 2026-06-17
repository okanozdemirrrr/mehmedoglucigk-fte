import { useEffect, useState, useCallback } from 'react';
import PageHeader from '../../components/ui/PageHeader';
import StatusBadge from '../../components/ui/StatusBadge';
import StatCard from '../../components/ui/StatCard';
import useOrderStore from '../../store/orderStore';
import { getCariBalance, getCariMovements } from '../../services/catalogApi';
import { formatCurrency, formatDate, formatDateShort } from '../../utils/format';

const isCreditMovement = (row) =>
  row.transaction_type === 'PAYMENT' || Number(row.amount) < 0;

const OrderTracking = () => {
  const { orders, fetchOrders, confirmDelivery, isLoading, error: ordersError } = useOrderStore();
  const [cariLoading, setCariLoading] = useState(true);
  const [cariError, setCariError] = useState(null);
  const [balance, setBalance] = useState(0);
  const [movements, setMovements] = useState([]);
  const [confirmingId, setConfirmingId] = useState(null);
  const [confirmError, setConfirmError] = useState(null);

  const loadCari = useCallback(() => {
    setCariLoading(true);
    setCariError(null);
    return Promise.all([getCariBalance(), getCariMovements()])
      .then(([balanceData, movementData]) => {
        setBalance(Number(balanceData.balance) || 0);
        setMovements(Array.isArray(movementData) ? movementData : []);
      })
      .catch((err) => {
        setBalance(0);
        setMovements([]);
        setCariError(
          err.response?.data?.detail ||
            err.response?.data?.error ||
            'Cari hesap verileri yüklenemedi.'
        );
      })
      .finally(() => setCariLoading(false));
  }, []);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    loadCari();
  }, [loadCari]);

  const sortedOrders = [...orders].sort(
    (a, b) => new Date(b.order_date) - new Date(a.order_date)
  );

  const lastPayment = movements.find((row) => row.transaction_type === 'PAYMENT');

  const handleConfirmDelivery = async (orderId) => {
    setConfirmError(null);
    setConfirmingId(orderId);
    try {
      await confirmDelivery(orderId);
      await loadCari();
    } catch (err) {
      setConfirmError(
        err.response?.data?.error ||
          err.response?.data?.detail ||
          'Teslim onayı gönderilemedi.'
      );
    } finally {
      setConfirmingId(null);
    }
  };

  return (
    <div>
      <PageHeader
        title="Sipariş Takip & Cari"
        subtitle="Geçmiş siparişleriniz ve güncel borç durumu"
      />

      {(ordersError || cariError || confirmError) && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {confirmError || ordersError || cariError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <StatCard
          label="Güncel Bakiye / Borç"
          value={cariLoading ? '...' : formatCurrency(Math.max(balance, 0))}
        />
        <StatCard
          label="Son Tahsilat"
          value={
            cariLoading
              ? '...'
              : lastPayment
                ? formatCurrency(Math.abs(Number(lastPayment.amount)))
                : formatCurrency(0)
          }
          subtext={lastPayment ? formatDateShort(lastPayment.transaction_date) : 'Kayıt yok'}
        />
      </div>

      <div className="erp-card mb-6">
        <div className="px-4 py-3 border-b border-gray-300 bg-gray-50">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">
            Sipariş Geçmişi
          </h2>
        </div>
        {isLoading ? (
          <p className="p-6 text-sm text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="erp-table">
              <thead>
                <tr>
                  <th>Sipariş No</th>
                  <th>Tarih</th>
                  <th>İçerik</th>
                  <th>Tutar</th>
                  <th>Durum</th>
                  <th className="text-right">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {sortedOrders.map((order) => (
                  <tr key={order.id}>
                    <td className="font-semibold tabular-nums">{order.order_number}</td>
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
                    <td className="text-right whitespace-nowrap">
                      {order.status === 'ON_THE_WAY' ? (
                        <button
                          type="button"
                          onClick={() => handleConfirmDelivery(order.id)}
                          disabled={confirmingId === order.id}
                          className="erp-btn-confirm-delivery"
                        >
                          {confirmingId === order.id ? 'İşleniyor...' : 'Teslim Aldım'}
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
                {sortedOrders.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center text-gray-500 py-8">
                      Henüz sipariş bulunmamaktadır.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="erp-card">
        <div className="px-4 py-3 border-b border-gray-300 bg-gray-50">
          <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">
            Cari Hesap Hareketleri
          </h2>
        </div>
        {cariLoading ? (
          <p className="p-6 text-sm text-gray-500">Yükleniyor...</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="erp-table">
              <thead>
                <tr>
                  <th>Tarih</th>
                  <th>Tip</th>
                  <th>Açıklama</th>
                  <th className="text-right">Tutar</th>
                </tr>
              </thead>
              <tbody>
                {movements.map((row) => {
                  const isCredit = isCreditMovement(row);
                  return (
                    <tr key={row.id}>
                      <td className="tabular-nums text-gray-600">
                        {formatDateShort(row.transaction_date)}
                      </td>
                      <td>
                        <span
                          className={`text-xs font-semibold uppercase ${
                            isCredit ? 'text-green-700' : 'text-red-700'
                          }`}
                        >
                          {row.transaction_type_display || row.transaction_type}
                        </span>
                      </td>
                      <td className="text-gray-700">{row.description}</td>
                      <td
                        className={`text-right font-semibold tabular-nums ${
                          isCredit ? 'text-green-700' : 'text-gray-900'
                        }`}
                      >
                        {isCredit ? '−' : '+'}
                        {formatCurrency(Math.abs(Number(row.amount)))}
                      </td>
                    </tr>
                  );
                })}
                {movements.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-gray-500 py-8">
                      Cari hareket bulunamadı.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderTracking;
