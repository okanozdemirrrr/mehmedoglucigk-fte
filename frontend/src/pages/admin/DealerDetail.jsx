import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import PageHeader from '../../components/ui/PageHeader';
import Modal from '../../components/ui/Modal';
import {
  getDealer,
  getDealerPrices,
  getProducts,
  createDealerPrice,
  deleteDealerPrice,
  getCariMovements,
  receiveDealerPayment,
} from '../../services/catalogApi';
import { formatCurrency, formatDateShort } from '../../utils/format';

const DealerDetail = () => {
  const { id } = useParams();
  const [tab, setTab] = useState('info');
  const [dealer, setDealer] = useState(null);
  const [prices, setPrices] = useState([]);
  const [products, setProducts] = useState([]);
  const [cariMovements, setCariMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentSubmitting, setPaymentSubmitting] = useState(false);
  const [paymentError, setPaymentError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [form, setForm] = useState({
    product: '',
    price: '',
    valid_from: new Date().toISOString().slice(0, 10),
    valid_until: '',
  });

  const loadDealer = async () => {
    const dealerData = await getDealer(id);
    setDealer(dealerData);
    return dealerData;
  };

  const loadCari = async () => {
    const movementData = await getCariMovements(id);
    setCariMovements(Array.isArray(movementData) ? movementData : []);
  };

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [, priceData, productData] = await Promise.all([
        loadDealer(),
        getDealerPrices(id),
        getProducts(),
        loadCari(),
      ]);
      setPrices(Array.isArray(priceData) ? priceData : []);
      setProducts(Array.isArray(productData) ? productData : []);
    } catch (err) {
      setDealer(null);
      setPrices([]);
      setProducts([]);
      setCariMovements([]);
      setError(err.response?.data?.detail || err.response?.data?.error || 'Bayi bilgileri yüklenemedi.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const handleCreatePrice = async (e) => {
    e.preventDefault();
    if (!form.product || !form.price) return;
    try {
      await createDealerPrice({
        dealer: Number(id),
        product: Number(form.product),
        price: form.price,
        valid_from: form.valid_from,
        valid_until: form.valid_until || null,
      });
      setForm({ ...form, product: '', price: '', valid_until: '' });
      load();
    } catch {
      alert('Fiyat kaydedilemedi.');
    }
  };

  const handleDeletePrice = async (priceId) => {
    if (!window.confirm('Bu özel fiyat silinsin mi?')) return;
    try {
      await deleteDealerPrice(priceId);
      load();
    } catch {
      alert('Silinemedi.');
    }
  };

  const handleReceivePayment = async (e) => {
    e.preventDefault();
    setPaymentError(null);
    const amount = parseFloat(paymentAmount);
    if (!paymentAmount || Number.isNaN(amount) || amount <= 0) {
      setPaymentError('Geçerli bir tutar giriniz.');
      return;
    }

    setPaymentSubmitting(true);
    try {
      const result = await receiveDealerPayment(id, amount);
      setDealer((prev) =>
        prev ? { ...prev, current_balance: result.current_balance } : prev
      );
      await Promise.all([loadDealer(), loadCari()]);
      setPaymentModalOpen(false);
      setPaymentAmount('');
      setSuccessMessage(result.status || 'Tahsilat başarıyla işlendi');
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err) {
      setPaymentError(
        err.response?.data?.error ||
          err.response?.data?.detail ||
          'Tahsilat kaydedilemedi.'
      );
    } finally {
      setPaymentSubmitting(false);
    }
  };

  if (loading) {
    return <p className="text-sm text-gray-500">Yükleniyor...</p>;
  }

  if (error || !dealer) {
    return (
      <div>
        <PageHeader title="Bayi Profili" subtitle="Detay yüklenemedi" />
        <div className="erp-card p-6 text-center">
          <p className="text-sm text-gray-600 mb-4">{error || 'Bayi kaydı bulunamadı.'}</p>
          <Link to="/admin/bayiler" className="erp-btn-secondary">
            ← Listeye Dön
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={dealer.name}
        subtitle={`Bayi kodu: ${dealer.code}`}
        actions={
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setPaymentModalOpen(true);
                setPaymentAmount('');
                setPaymentError(null);
              }}
              className="erp-btn-primary"
            >
              Ödeme Al
            </button>
            <Link to="/admin/bayiler" className="erp-btn-secondary">
              ← Listeye Dön
            </Link>
          </div>
        }
      />

      {successMessage && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-green-800 bg-green-50 border border-green-200 rounded-sm">
          {successMessage}
        </div>
      )}

      <div className="flex gap-1 mb-4 border-b border-gray-300">
        {[
          { key: 'info', label: 'Genel Bilgi' },
          { key: 'pricing', label: 'Özel Fiyat Tanımla' },
        ].map(({ key, label }) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`px-4 py-2 text-xs font-semibold uppercase border-b-2 -mb-px rounded-sm ${
              tab === key
                ? 'border-bordo-800 text-bordo-800'
                : 'border-transparent text-gray-500 hover:text-gray-800'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === 'info' && (
        <div className="space-y-4">
          <div className="erp-card p-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-xs uppercase text-gray-500">Vergi No</p>
              <p className="font-medium">{dealer.tax_number || '—'}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-gray-500">Kredi Limiti</p>
              <p className="font-medium tabular-nums">{formatCurrency(dealer.credit_limit || 0)}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-gray-500">İskonto Oranı</p>
              <p className="font-medium">%{dealer.discount_rate || 0}</p>
            </div>
            <div>
              <p className="text-xs uppercase text-gray-500">Güncel Bakiye / Borç</p>
              <p className="font-bold tabular-nums text-bordo-800">
                {formatCurrency(Math.max(Number(dealer.current_balance) || 0, 0))}
              </p>
            </div>
            <div className="md:col-span-2">
              <p className="text-xs uppercase text-gray-500">Adres</p>
              <p className="font-medium">{dealer.address || `${dealer.city || ''} ${dealer.district || ''}`}</p>
            </div>
          </div>

          <div className="erp-card overflow-x-auto">
            <div className="px-4 py-3 border-b border-gray-300 bg-gray-50">
              <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">
                Cari Hesap Hareketleri
              </h2>
            </div>
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
                {cariMovements.map((row) => {
                  const isCredit = row.transaction_type === 'PAYMENT' || Number(row.amount) < 0;
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
                {cariMovements.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-gray-500 py-8">
                      Cari hareket bulunamadı.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {tab === 'pricing' && (
        <div className="space-y-4">
          <form onSubmit={handleCreatePrice} className="erp-card p-4">
            <h2 className="text-xs font-bold uppercase text-gray-700 mb-3">Yeni Özel Fiyat</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <select
                value={form.product}
                onChange={(e) => setForm({ ...form, product: e.target.value })}
                className="erp-input"
                required
              >
                <option value="">Ürün seçin</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.code} — {p.name}
                  </option>
                ))}
              </select>
              <input
                type="number"
                step="0.01"
                placeholder="Özel fiyat"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
                className="erp-input"
                required
              />
              <input
                type="date"
                value={form.valid_from}
                onChange={(e) => setForm({ ...form, valid_from: e.target.value })}
                className="erp-input"
                required
              />
              <button type="submit" className="erp-btn-primary">Kaydet</button>
            </div>
          </form>

          <div className="erp-card overflow-x-auto">
            <table className="erp-table">
              <thead>
                <tr>
                  <th>Ürün</th>
                  <th>Özel Fiyat</th>
                  <th>Geçerlilik</th>
                  <th className="text-right">İşlem</th>
                </tr>
              </thead>
              <tbody>
                {prices.map((row) => (
                  <tr key={row.id}>
                    <td>{row.product_name}</td>
                    <td className="font-semibold tabular-nums">{formatCurrency(row.price)}</td>
                    <td className="text-gray-600 text-xs tabular-nums">
                      {row.valid_from} — {row.valid_until || 'Süresiz'}
                    </td>
                    <td className="text-right">
                      <button
                        type="button"
                        onClick={() => handleDeletePrice(row.id)}
                        className="erp-btn-secondary text-red-700"
                      >
                        Sil
                      </button>
                    </td>
                  </tr>
                ))}
                {prices.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center text-gray-500 py-6">
                      Bu bayi için özel fiyat tanımlı değil.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal
        open={paymentModalOpen}
        onClose={() => !paymentSubmitting && setPaymentModalOpen(false)}
        title="Tahsilat Gir"
        footer={
          <>
            <button
              type="button"
              onClick={() => setPaymentModalOpen(false)}
              disabled={paymentSubmitting}
              className="erp-btn-secondary"
            >
              İptal
            </button>
            <button
              type="submit"
              form="payment-form"
              disabled={paymentSubmitting}
              className="erp-btn-primary"
            >
              {paymentSubmitting ? 'Kaydediliyor...' : 'Kaydet'}
            </button>
          </>
        }
      >
        <form id="payment-form" onSubmit={handleReceivePayment}>
          <label className="block text-xs font-semibold uppercase text-gray-600 mb-2">
            Alınan ödeme miktarını (TL) giriniz:
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            required
            value={paymentAmount}
            onChange={(e) => setPaymentAmount(e.target.value)}
            className="erp-input"
            placeholder="0,00"
            autoFocus
          />
          {paymentError && (
            <p className="mt-2 text-xs text-red-700">{paymentError}</p>
          )}
        </form>
      </Modal>
    </div>
  );
};

export default DealerDetail;
