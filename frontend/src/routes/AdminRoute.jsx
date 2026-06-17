import { Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const AdminRoute = () => {
  const token = useAuthStore((s) => s.token) || localStorage.getItem('token');
  const user = useAuthStore((s) => s.user) || JSON.parse(localStorage.getItem('user') || 'null');

  if (!token) return <Navigate to="/login" replace />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.is_distributor) return <Navigate to="/bayi/siparis-olustur" replace />;

  return <Outlet />;
};

export default AdminRoute;
