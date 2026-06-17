import { create } from 'zustand';
import api from '../services/api';

const unwrapList = (data) => (data.results ? data.results : data);

const useOrderStore = create((set, get) => ({
  orders: [],
  isLoading: false,
  error: null,

  fetchOrders: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.get('orders/orders/');
      const data = unwrapList(response.data);
      set({ orders: Array.isArray(data) ? data : [], isLoading: false, error: null });
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        error.response?.data?.error ||
        'Siparişler yüklenemedi.';
      set({ orders: [], isLoading: false, error: message });
    }
  },

  createOrder: async (items, notes = 'Bayi panelinden oluşturuldu') => {
    await api.post('orders/orders/', { notes, items });
    await get().fetchOrders();
  },

  updateOrderStatus: async (orderId, action) => {
    await api.post(`orders/orders/${orderId}/${action}/`);
    await get().fetchOrders();
  },

  confirmDelivery: async (orderId) => {
    await api.post(`orders/orders/${orderId}/confirm_delivery/`);
    await get().fetchOrders();
  },
}));

export default useOrderStore;
