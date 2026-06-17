import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const user = await useAuthStore.getState().login(email, password);
      if (user.is_distributor) {
        navigate('/admin/dashboard');
      } else {
        navigate('/bayi/siparis-olustur');
      }
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        (err.message === 'Network Error' ? 'Sunucuya bağlanılamadı. Backend çalışıyor mu?' : 'Giriş başarısız.');
      setError(msg);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="bg-bordo-800 px-6 py-8 border border-bordo-950">
          <p className="text-xl font-bold tracking-[0.25em] text-white text-center">MEHMEDOĞLU ÇİĞKÖFTE</p>
        </div>

        <div className="bg-white border border-t-0 border-gray-300 px-6 py-6">
          <h2 className="text-sm font-bold uppercase tracking-wide text-gray-800 mb-5">
            Sistem Girişi
          </h2>

          {error && (
            <div className="mb-4 px-3 py-2 text-xs font-medium text-red-800 bg-red-50 border border-red-200 rounded-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                E-posta
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="erp-input"
                placeholder="eposta@sirket.com"
                autoComplete="email"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                Şifre
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="erp-input"
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </div>

            <button type="submit" disabled={isLoading} className="erp-btn-primary w-full mt-2">
              {isLoading ? 'Doğrulanıyor...' : 'Giriş Yap'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-gray-600">
            Bayimiz mi olmak istiyorsunuz?{' '}
            <Link
              to="/bayi-basvuru"
              className="text-[#580F1C] font-semibold hover:underline"
            >
              Hemen Başvuru yap
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

export default Login;
