import { Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const DealerRoute = () => {
  const token = useAuthStore((s) => s.token) || localStorage.getItem('token');
  const user = useAuthStore((s) => s.user) || JSON.parse(localStorage.getItem('user') || 'null');

  if (!token) return <Navigate to="/login" replace />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.is_distributor || user.role !== 'DEALER') {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return <Outlet />;
};

export default DealerRoute;
