import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import useAuthStore from '../../store/authStore';

const SIDEBAR_WIDTH = 'w-56';

const AdminLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { name: 'Finansal Özet', path: '/admin/dashboard' },
    { name: 'Gelen Talepler', path: '/admin/siparisler' },
    { name: 'Geçmiş Siparişler', path: '/admin/gecmis-siparisler' },
    { name: 'Bayi Yönetimi', path: '/admin/bayiler' },
    { name: 'Stok & Ürünler', path: '/admin/stok' },
  ];

  const displayName = user?.email || 'Kullanıcı';
  const roleLabel = user?.role_display || 'Yönetici';

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className={`${SIDEBAR_WIDTH} flex-shrink-0 bg-bordo-800 text-white flex flex-col border-r border-bordo-950`}>
        <div className="px-4 py-5 border-b border-bordo-950">
          <p className="text-base font-bold tracking-[0.2em] text-white">MERGEN</p>
          <p className="text-[10px] uppercase tracking-widest text-gray-400 mt-1">Kurumsal ERP</p>
        </div>

        <nav className="flex-1 py-3">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={isActive ? 'erp-sidebar-link-active' : 'erp-sidebar-link'}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="px-4 py-3 border-t border-bordo-950 text-[10px] text-gray-500 uppercase tracking-wider">
          Mergen Teknoloji v1.0
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-12 flex-shrink-0 bg-white border-b border-gray-300 flex items-center justify-between px-6">
          <span className="text-xs font-semibold uppercase tracking-wide text-gray-600">
            Dağıtıcı Operasyon Merkezi
          </span>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-900 capitalize">{displayName}</p>
              <p className="text-[10px] uppercase text-gray-500">{roleLabel}</p>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="erp-btn-secondary text-xs"
            >
              Çıkış Yap
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
