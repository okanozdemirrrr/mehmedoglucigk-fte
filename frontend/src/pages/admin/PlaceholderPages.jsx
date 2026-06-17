import PageHeader from '../../components/ui/PageHeader';

const PlaceholderPage = ({ title, description }) => (  <div>
    <PageHeader title={title} subtitle={description} />
    <div className="erp-card p-8 text-center">
      <p className="text-sm text-gray-600">Bu modül geliştirme aşamasında.</p>
      <p className="text-xs text-gray-400 mt-2">Backend entegrasyonu sonraki sprintte tamamlanacak.</p>
    </div>
  </div>
);

export const AdminStock = () => (  <PlaceholderPage title="Stok & Ürünler" description="Ürün kataloğu, stok seviyeleri ve fiyat listeleri" />
);

export default PlaceholderPage;
