import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../../components/ui/PageHeader';
import { getDealers } from '../../services/catalogApi';
import { formatCurrency } from '../../utils/format';

const Dealers = () => {
  const [dealers, setDealers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getDealers()
      .then((data) => {
        setDealers(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        setDealers([]);
        setError(err.response?.data?.detail || 'Bayi listesi yüklenemedi.');
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <PageHeader
        title="Bayi Yönetimi"
        subtitle="Bayi kartları, limit ve özel fiyat tanımları"
      />

      {error && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {error}
        </div>
      )}

      <div className="erp-card overflow-x-auto">
        {loading ? (
          <p className="p-6 text-sm text-gray-500">Yükleniyor...</p>
        ) : (
          <table className="erp-table">
            <thead>
              <tr>
                <th>Kod</th>
                <th>Bayi Adı</th>
                <th>Şehir</th>
                <th>Kredi Limiti</th>
                <th>Bakiye</th>
                <th>Durum</th>
                <th className="text-right">İşlem</th>
              </tr>
            </thead>
            <tbody>
              {dealers.map((dealer) => (
                <tr key={dealer.id}>
                  <td className="font-semibold tabular-nums">{dealer.code}</td>
                  <td className="font-medium">{dealer.name}</td>
                  <td className="text-gray-600">{dealer.city || '—'}</td>
                  <td className="tabular-nums">{formatCurrency(dealer.credit_limit || 0)}</td>
                  <td className="tabular-nums font-semibold">
                    {formatCurrency(dealer.current_balance || 0)}
                  </td>
                  <td>
                    <span
                      className={`text-xs font-semibold uppercase ${
                        dealer.is_active ? 'text-green-700' : 'text-gray-400'
                      }`}
                    >
                      {dealer.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                  </td>
                  <td className="text-right">
                    <Link to={`/admin/bayiler/${dealer.id}`} className="erp-btn-secondary inline-block">
                      Profil
                    </Link>
                  </td>
                </tr>
              ))}
              {dealers.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center text-gray-500 py-8">
                    Kayıtlı bayi bulunmamaktadır.
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

export default Dealers;
