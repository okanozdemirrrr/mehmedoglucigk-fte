import { useState, useEffect } from 'react';
import PageHeader from '../../components/ui/PageHeader';
import ProductOptionModal from '../../components/products/ProductOptionModal';
import useCartStore from '../../store/cartStore';
import useOrderStore from '../../store/orderStore';
import { getCatalog } from '../../services/catalogApi';
import { formatCurrency } from '../../utils/format';

const CreateOrder = () => {
  const { createOrder } = useOrderStore();
  const lines = useCartStore((s) => s.lines);
  const addLine = useCartStore((s) => s.addLine);
  const removeLine = useCartStore((s) => s.removeLine);
  const clearCart = useCartStore((s) => s.clearCart);
  const toOrderItems = useCartStore((s) => s.toOrderItems);
  const getGrandTotal = useCartStore((s) => s.getGrandTotal);

  const [products, setProducts] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState(null);
  const [modalProduct, setModalProduct] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setCatalogLoading(true);
    setCatalogError(null);
    getCatalog()
      .then((data) => {
        setProducts(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        setProducts([]);
        setCatalogError(
          err.response?.data?.detail || 'Ürün kataloğu yüklenemedi.'
        );
      })
      .finally(() => setCatalogLoading(false));
  }, []);

  const openModal = (product) => {
    if (product.option_groups?.length > 0) {
      setModalProduct(product);
    } else {
      addLine({
        product,
        quantity: 1,
        selectedOptions: [],
        unitPrice: parseFloat(product.effective_price || product.base_price),
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (lines.length === 0) return;

    setIsSubmitting(true);
    try {
      await createOrder(toOrderItems());
      clearCart();
      alert('Sipariş talebiniz alındı. Onay bekliyor.');
    } catch (error) {
      const msg =
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Sipariş gönderilemedi. Bayi hesabıyla giriş yaptığınızdan emin olun.';
      alert(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Sipariş Oluştur"
        subtitle="Ürün seçin, opsiyonları belirleyin ve sepeti onaylayın"
      />

      {catalogError && (
        <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
          {catalogError}
        </div>
      )}

      <div className="erp-card mb-4">
        <div className="px-4 py-2 border-b border-gray-300 bg-gray-50">
          <div className="grid grid-cols-12 gap-2 text-xs font-semibold uppercase text-gray-600">
            <span className="col-span-2">Kod</span>
            <span className="col-span-5">Ürün</span>
            <span className="col-span-2">Fiyatınız</span>
            <span className="col-span-1">Birim</span>
            <span className="col-span-2 text-right">İşlem</span>
          </div>
        </div>
        {catalogLoading ? (
          <p className="p-6 text-sm text-gray-500">Katalog yükleniyor...</p>
        ) : products.length === 0 ? (
          <p className="p-6 text-sm text-gray-500 text-center">
            Katalogda görüntülenecek ürün bulunmamaktadır.
          </p>
        ) : (
          <div className="divide-y divide-gray-200">
            {products.map((product) => (
              <div key={product.id} className="grid grid-cols-12 gap-2 items-center px-4 py-3">
                <span className="col-span-2 text-xs text-gray-500 tabular-nums">{product.code}</span>
                <div className="col-span-5">
                  <p className="text-sm font-medium text-gray-900">{product.name}</p>
                  {product.option_groups?.length > 0 && (
                    <p className="text-[10px] text-gray-500 uppercase mt-0.5">Opsiyon seçimi gerekli</p>
                  )}
                </div>
                <span className="col-span-2 text-sm tabular-nums font-semibold">
                  {formatCurrency(product.effective_price || product.base_price)}
                </span>
                <span className="col-span-1 text-xs text-gray-500 uppercase">{product.unit}</span>
                <div className="col-span-2 text-right">
                  <button type="button" onClick={() => openModal(product)} className="erp-btn-secondary">
                    Sepete Ekle
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {lines.length > 0 && (
        <form onSubmit={handleSubmit}>
          <div className="erp-card mb-4">
            <div className="px-4 py-3 border-b border-gray-300 bg-gray-50">
              <h2 className="text-xs font-bold uppercase tracking-wide text-gray-700">Sepet</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {lines.map((line) => (
                <div key={line.id} className="px-4 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div>
                    <p className="text-sm font-semibold">{line.productName}</p>
                    <p className="text-xs text-gray-500">
                      {line.quantity} {line.unit} × {formatCurrency(line.unitPrice)}
                    </p>
                    {line.selectedOptions?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {line.selectedOptions.map((opt) => (
                          <span
                            key={`${opt.option_id}-${opt.option_name}`}
                            className="text-[10px] font-semibold uppercase px-1.5 py-0.5 border border-gray-300 bg-gray-50 text-gray-700 rounded-sm"
                          >
                            {opt.option_name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold tabular-nums">{formatCurrency(line.lineTotal)}</span>
                    <button type="button" onClick={() => removeLine(line.id)} className="erp-btn-secondary text-red-700">
                      Kaldır
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="erp-card p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <p className="text-xs uppercase font-semibold text-gray-500">Sipariş Toplamı</p>
              <p className="text-2xl font-bold text-gray-900 tabular-nums mt-1">
                {formatCurrency(getGrandTotal())}
              </p>
              <p className="text-xs text-gray-500 mt-1">{lines.length} kalem · KDV hariç</p>
            </div>
            <button type="submit" disabled={isSubmitting} className="erp-btn-primary px-8 py-3">
              {isSubmitting ? 'Gönderiliyor...' : 'Siparişi Onayla'}
            </button>
          </div>
        </form>
      )}

      <ProductOptionModal
        product={modalProduct}
        open={Boolean(modalProduct)}
        onClose={() => setModalProduct(null)}
        onAddToCart={addLine}
      />
    </div>
  );
};

export default CreateOrder;
