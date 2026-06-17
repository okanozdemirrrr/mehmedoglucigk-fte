import { useState } from 'react';
import { Link } from 'react-router-dom';

const initialForm = {
  companyName: '',
  contactName: '',
  phone: '',
  taxOffice: '',
  taxNumber: '',
  cityDistrict: '',
};

const BayiBasvuru = () => {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSuccessMessage('');

    // Şimdilik sadece UI — backend entegrasyonu sonra eklenecek
    await new Promise((resolve) => setTimeout(resolve, 400));

    setSuccessMessage(
      'Başvurunuz alınmıştır, yöneticilerimiz sizinle iletişime geçecektir.'
    );
    setForm(initialForm);
    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="bg-bordo-800 px-6 py-8 border border-bordo-950">
          <p className="text-xl font-bold tracking-[0.25em] text-white text-center">MERGEN</p>
          <p className="text-[10px] uppercase tracking-widest text-gray-400 text-center mt-2">
            Bayilik Başvuru Formu
          </p>
        </div>

        <div className="bg-white border border-t-0 border-gray-300 px-6 py-6">
          <h2 className="text-sm font-bold uppercase tracking-wide text-[#580F1C] mb-1">
            Bayilik Başvurusu
          </h2>
          <p className="text-xs text-gray-500 mb-5">
            Formu doldurun; ekibimiz başvurunuzu inceleyip sizinle iletişime geçecektir.
          </p>

          {successMessage && (
            <div className="mb-4 px-3 py-2 text-xs font-medium text-green-800 bg-green-50 border border-green-200 rounded-sm">
              {successMessage}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                Dükkan / Firma Adı
              </label>
              <input
                type="text"
                name="companyName"
                required
                value={form.companyName}
                onChange={handleChange}
                className="erp-input"
                placeholder="Örn: Mehmetoğlu Çiğköfte"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                Yetkili Adı Soyadı
              </label>
              <input
                type="text"
                name="contactName"
                required
                value={form.contactName}
                onChange={handleChange}
                className="erp-input"
                placeholder="Ad Soyad"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                Telefon Numarası
              </label>
              <input
                type="tel"
                name="phone"
                required
                value={form.phone}
                onChange={handleChange}
                className="erp-input"
                placeholder="05XX XXX XX XX"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                  Vergi Dairesi
                </label>
                <input
                  type="text"
                  name="taxOffice"
                  required
                  value={form.taxOffice}
                  onChange={handleChange}
                  className="erp-input"
                  placeholder="Vergi dairesi"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                  Vergi No
                </label>
                <input
                  type="text"
                  name="taxNumber"
                  required
                  value={form.taxNumber}
                  onChange={handleChange}
                  className="erp-input"
                  placeholder="Vergi numarası"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                İl / İlçe
              </label>
              <input
                type="text"
                name="cityDistrict"
                required
                value={form.cityDistrict}
                onChange={handleChange}
                className="erp-input"
                placeholder="Örn: İstanbul / Kadıköy"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="erp-btn-primary w-full mt-2"
            >
              {isSubmitting ? 'Gönderiliyor...' : 'Başvuruyu Gönder'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-gray-600">
            Zaten hesabınız var mı?{' '}
            <Link to="/login" className="text-[#580F1C] font-semibold hover:underline">
              Giriş yapın
            </Link>
          </p>
        </div>

        <p className="mt-4 text-center text-[10px] uppercase tracking-wider text-gray-500">
          © {new Date().getFullYear()} Mergen Teknoloji
        </p>
      </div>
    </div>
  );
};

export default BayiBasvuru;
