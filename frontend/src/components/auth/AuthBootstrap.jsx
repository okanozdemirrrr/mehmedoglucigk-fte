import { useEffect, useState } from 'react';
import useAuthStore from '../../store/authStore';

/** Token varsa kullanıcı bilgisini users tablosundan (/accounts/me/) yeniler */
const AuthBootstrap = ({ children }) => {
  const fetchCurrentUser = useAuthStore((s) => s.fetchCurrentUser);
  const [ready, setReady] = useState(() => !localStorage.getItem('token'));

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      setReady(true);
      return;
    }

    fetchCurrentUser().finally(() => setReady(true));
  }, [fetchCurrentUser]);

  if (!ready) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-xs uppercase tracking-widest text-gray-500">Yükleniyor...</p>
      </div>
    );
  }

  return children;
};

export default AuthBootstrap;
