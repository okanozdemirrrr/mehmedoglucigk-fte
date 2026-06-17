import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthBootstrap from './components/auth/AuthBootstrap';
import Login from './pages/auth/Login';
import BayiBasvuru from './pages/BayiBasvuru';
import AdminLayout from './components/layout/AdminLayout';
import DealerLayout from './components/layout/DealerLayout';
import AdminDashboard from './pages/admin/Dashboard';
import AdminOrders from './pages/admin/Orders';
import PastOrders from './pages/admin/PastOrders';
import Dealers from './pages/admin/Dealers';
import DealerDetail from './pages/admin/DealerDetail';
import { AdminStock } from './pages/admin/PlaceholderPages';
import CreateOrder from './pages/bayi/CreateOrder';
import OrderTracking from './pages/bayi/OrderTracking';
import ProtectedRoute from './routes/ProtectedRoute';
import AdminRoute from './routes/AdminRoute';
import DealerRoute from './routes/DealerRoute';

function App() {
  return (
    <AuthBootstrap>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/bayi-basvuru" element={<BayiBasvuru />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AdminRoute />}>
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<Navigate to="dashboard" replace />} />
              <Route path="dashboard" element={<AdminDashboard />} />
              <Route path="siparisler" element={<AdminOrders />} />
              <Route path="gecmis-siparisler" element={<PastOrders />} />
              <Route path="bayiler" element={<Dealers />} />
              <Route path="bayiler/:id" element={<DealerDetail />} />
              <Route path="stok" element={<AdminStock />} />
            </Route>
          </Route>

          <Route element={<DealerRoute />}>
            <Route path="/bayi" element={<DealerLayout />}>
              <Route index element={<Navigate to="siparis-olustur" replace />} />
              <Route path="siparis-olustur" element={<CreateOrder />} />
              <Route path="siparislerim" element={<OrderTracking />} />
              <Route path="dashboard" element={<Navigate to="siparis-olustur" replace />} />
            </Route>
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
    </AuthBootstrap>
  );
}

export default App;
